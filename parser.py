import json
import re

import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    ),
    "Accept-Language": "pt-PT,pt;q=0.9,en;q=0.8",
}


def extrair_meta(soup, nome):
    tag = soup.find("meta", attrs={"property": nome})

    if tag and tag.get("content"):
        return tag["content"].strip()

    tag = soup.find("meta", attrs={"name": nome})

    if tag and tag.get("content"):
        return tag["content"].strip()

    return None


def extrair_json_ld(soup):
    scripts = soup.find_all(
        "script",
        type="application/ld+json"
    )

    for script in scripts:
        texto = script.string or script.get_text()

        if not texto:
            continue

        try:
            data = json.loads(texto)
        except (json.JSONDecodeError, TypeError):
            continue

        objetos = []

        if isinstance(data, dict):
            objetos.append(data)

            if isinstance(data.get("@graph"), list):
                objetos.extend(data["@graph"])

        elif isinstance(data, list):
            objetos.extend(data)

        for produto in objetos:
            if not isinstance(produto, dict):
                continue

            tipo = produto.get("@type")

            if isinstance(tipo, list):
                eh_produto = "Product" in tipo
            else:
                eh_produto = tipo == "Product"

            if not eh_produto:
                continue

            nome = produto.get("name")
            imagem = produto.get("image")
            if isinstance(imagem, list):
                imagem = imagem[0] if imagem else None

            preco = None
            moeda = None

            offers = produto.get("offers")

            if isinstance(offers, dict):
                preco = offers.get("price")
                moeda = offers.get("priceCurrency")

            return {
                "name": nome,
                "price": preco,
                "currency": moeda,
                "image_url": imagem,
            }

    return None


def extrair_open_graph(soup):
    return {
        "name": extrair_meta(soup, "og:title"),
        "price": extrair_meta(soup, "product:price:amount"),
        "currency": extrair_meta(soup, "product:price:currency"),
        "image_url": extrair_meta(soup, "og:image"),
    }


def extrair_amazon(soup):
    """
    Tenta extrair dados de páginas Amazon
    a partir das estruturas presentes no HTML.
    """

    html = str(soup)

    nome = None
    preco = None
    moeda = None
    imagem = None

    # ---------------------------------------------------------
    # NOME
    # ---------------------------------------------------------

    # Método 1: elemento #productTitle
    titulo = soup.find(id="productTitle")

    if titulo:
        nome = titulo.get_text(" ", strip=True)

    # Método 2: título da página
    if not nome and soup.title:
        titulo_texto = soup.title.get_text(" ", strip=True)

        if ": Amazon" in titulo_texto:
            nome = titulo_texto.split(": Amazon", 1)[0].strip()

    # ---------------------------------------------------------
    # PREÇO
    # ---------------------------------------------------------

    # A Amazon inclui frequentemente:
    #
    # "priceAmount":12.69
    #
    match = re.search(
        r'"priceAmount"\s*:\s*([0-9]+(?:\.[0-9]+)?)',
        html
    )

    if match:
        preco = match.group(1)

    # Tentar moeda associada ao preço
    match = re.search(
        r'"currencySymbol"\s*:\s*"([^"]+)"',
        html
    )

    if match:
        simbolo = match.group(1)

        simbolos = {
            "€": "EUR",
            "$": "USD",
            "£": "GBP",
        }

        moeda = simbolos.get(simbolo, simbolo)

    # ---------------------------------------------------------
    # IMAGEM
    # ---------------------------------------------------------

    # Tentar imagem principal da página
    imagem_tag = soup.find(
        id="landingImage"
    )

    if imagem_tag:
        imagem = (
            imagem_tag.get("src")
            or imagem_tag.get("data-old-hires")
        )

    # Fallback: data-old-hires
    if not imagem:
        imagem_tag = soup.find(
            attrs={"data-old-hires": True}
        )

        if imagem_tag:
            imagem = imagem_tag.get("data-old-hires")

    # Fallback: Open Graph
    if not imagem:
        imagem = extrair_meta(soup, "og:image")

    return {
        "name": nome,
        "price": preco,
        "currency": moeda,
        "image_url": imagem,
    }


def combinar(dados_principais, dados_fallback):
    """
    Preenche campos vazios usando os dados de fallback.
    """

    resultado = dados_principais.copy()

    for campo in resultado:
        if not resultado[campo]:
            resultado[campo] = dados_fallback.get(campo)

    return resultado

def extrair_tradeinn(soup):
    """
    Tenta extrair dados de páginas Tradeinn/Goalinn
    a partir da meta description e Open Graph.
    """

    descricao = extrair_meta(soup, "description")

    preco = None

    if descricao:
        match = re.search(
            r'por\s+([0-9]+(?:[.,][0-9]+)?)\s*€',
            descricao,
            re.IGNORECASE
        )

        if match:
            preco = match.group(1).replace(",", ".")

    return {
        "name": extrair_meta(soup, "og:title"),
        "price": preco,
        "currency": "EUR" if preco else None,
        "image_url": extrair_meta(soup, "og:image"),
    }

def extrair_produto(url):
    resposta = requests.get(
        url,
        headers=HEADERS,
        timeout=10
    )

    resposta.raise_for_status()

    soup = BeautifulSoup(
        resposta.text,
        "html.parser"
    )

    # ---------------------------------------------------------
    # 1. JSON-LD
    # ---------------------------------------------------------

    produto = extrair_json_ld(soup)

    if produto:
        og = extrair_open_graph(soup)
        return combinar(produto, og)

    # ---------------------------------------------------------
    # 2. Amazon
    # ---------------------------------------------------------

    # 2. Amazon
    if "amazon." in resposta.url.lower():
        produto = extrair_amazon(soup)

        if any(produto.values()):
            return produto

    # 3. Tradeinn
    if "tradeinn.com" in resposta.url.lower():
        produto = extrair_tradeinn(soup)

        if any(produto.values()):
            return produto

    # ---------------------------------------------------------
    # 3. Open Graph
    # ---------------------------------------------------------

    return extrair_open_graph(soup)


if __name__ == "__main__":
    url = input("URL: ").strip()
    

    try:
        produto = extrair_produto(url)

        print("\nResultado:")
        print(f"Nome:     {produto['name']}")
        print(f"Preço:    {produto['price']}")
        print(f"Moeda:    {produto['currency']}")
        print(f"Imagem:   {produto['image_url']}")

    except requests.RequestException as e:
        print(f"\nErro ao aceder à página: {e}")

    except Exception as e:
        print(f"\nErro ao analisar a página: {e}")

        


# Wishlist App

Aplicação pessoal para gerir uma wishlist de objetos, viagens e outros interesses, com controlo de orçamento e extração automática de dados (nome, preço e imagem) a partir de um link.

## Objetivo

Guardar tudo o que quero comprar/fazer num só sítio, acompanhar quanto já tenho poupado, e conseguir colar um link de uma loja/site e a app extrair automaticamente o nome, preço e imagem do produto.

## Roteiro

- [x] **Fase 1 — MVP local:** base de dados + site simples onde adiciono itens manualmente (CRUD completo + CSS)
- [x] **Fase 2 — Orçamento:** mealheiro único (adicionar/retirar dinheiro), compra de itens a debitar do saldo, e sugestão de compra baseada em prioridade + orçamento (algoritmo de knapsack 0/1)
- [x] **Fase 3 — Parsing de links:** dado um URL, extrair nome/preço/imagem automaticamente e pré-preencher o formulário de adicionar item
- [ ] **Fase 4 — Mobile:** empacotar para Android e, mais tarde, iOS

*(Este projeto está a ser construído de forma incremental — cada fase só avança depois da anterior estar sólida.)*

## Stack

- **Backend:** Python + Flask
- **Base de dados:** SQLite
- **Parsing de páginas:** `requests` + `BeautifulSoup`
- **Frontend:** HTML + CSS (sem frameworks JS para já)

## Estrutura do projeto

```
wishlist-app/
├── app.py              # aplicação Flask (rotas)
├── database.py         # ligação e queries à base de dados
├── suggestions.py      # algoritmo de sugestão de compra (knapsack 0/1)
├── parser.py           # extração de nome/preço/imagem a partir de um URL
├── schema.sql          # definição das tabelas
├── init_db.py          # (re)cria a base de dados a partir do schema.sql
├── wishlist.db         # ficheiro da base de dados (gerado)
├── templates/
│   ├── index.html      # lista de itens
│   ├── add.html        # analisar link + formulário de adicionar item
│   └── edit.html       # formulário de editar item
├── static/
│   └── style.css
├── tests/
│   └── test_parser.py  # testes da normalização de preço e imagem
├── requirements.txt
└── README.md
```

## Modelo de dados

**items**

| campo         | tipo    | descrição                              |
|---------------|---------|-----------------------------------------|
| id            | INTEGER | chave primária                          |
| name          | TEXT    | nome do item                            |
| category      | TEXT    | "objeto", "viagem" ou "interesse"       |
| price         | REAL    | preço estimado                          |
| url           | TEXT    | link do produto (opcional)              |
| image_url     | TEXT    | imagem (opcional)                       |
| notes         | TEXT    | notas livres                            |
| priority      | INTEGER | usado para ordenar a wishlist e nas sugestões de compra |
| purchased     | INTEGER | 0 = por comprar, 1 = já comprado        |
| purchased_at  | TEXT    | data em que foi marcado como comprado   |
| created_at    | TEXT    | data de criação                         |

**movements** (histórico de entradas/saídas do mealheiro; o saldo atual é a soma de todos os `amount`)

| campo       | tipo    | descrição                                              |
|-------------|---------|----------------------------------------------------------|
| id          | INTEGER | chave primária                                          |
| amount      | REAL    | positivo = depósito, negativo = retirada ou compra      |
| type        | TEXT    | "deposit", "withdrawal" ou "purchase"                   |
| item_id     | INTEGER | preenchido apenas quando `type = "purchase"`             |
| note        | TEXT    | nota opcional                                            |
| created_at  | TEXT    | data do movimento                                        |

## Como correr localmente

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 init_db.py     # cria/recria a base de dados a partir do schema.sql
python3 app.py
```

A app fica disponível em `http://127.0.0.1:5000`.

Para correr os testes do parser (a partir da raiz do projeto):

```bash
python3 -m tests.test_parser
```

## Funcionalidades da Fase 2

- **Sugestão de compra na página principal:** dado o saldo atual, o algoritmo de knapsack 0/1 escolhe os itens (por comprar) que maximizam a prioridade total sem ultrapassar o saldo disponível
- **Mealheiro:** um único formulário permite depositar ou retirar dinheiro (rota `/movimento`), guardando cada movimento em `movements`
- **Saldo nunca negativo:** uma retirada superior ao saldo é bloqueada e mostra uma mensagem de erro
- **Marcar como comprado:** cada item por comprar tem um botão que o marca como comprado, define `purchased_at` e regista automaticamente o movimento de compra (dedução do saldo)

## Funcionalidades da Fase 3

Na página de adicionar item, colar o link de um produto e carregar em **Analisar** pré-preenche o formulário com o nome, preço, imagem e link. O utilizador revê (e corrige, se necessário) e só depois carrega em **Guardar** — nada é guardado automaticamente.

### Como o parser funciona

O `parser.py` tenta, por esta ordem:

1. **JSON-LD** (`Product`): nome, preço, moeda e imagem
2. **Amazon:** parser específico, porque as páginas não expõem os dados de produto em JSON-LD
3. **Tradeinn / Goalinn:** parser específico, que lê o preço a partir da `meta description`
4. **Open Graph** (`og:title`, `og:image`, `product:price:*`): fallback genérico

Os campos em falta num método são completados com Open Graph sempre que possível.

A função pública `extrair_produto(url)` devolve sempre dados normalizados:

- **preço** como `float` (aceita formatos como `29.99`, `29,99`, `1.299,99` ou `29,99 €`), ou `None`
- **imagem** como uma única string com o URL (lida com listas e objetos `ImageObject`), ou `None`

### Sites que bloqueiam pedidos (403)

Alguns sites (por exemplo Decathlon, Sprinter e Adidas) bloqueiam pedidos automáticos e devolvem `403 Forbidden`. Isto não é tratado como erro do parser: a app mostra um aviso e o utilizador preenche os dados manualmente. Não há regras para contornar bloqueios.

### Limitações conhecidas

- A moeda não é convertida: o preço de um site que não use euros é guardado tal como vem
- Um preço com um único ponto e sem vírgula (por exemplo `"1.299"`) é lido como decimal
- Cada site novo pode exigir um parser específico

## Estado atual

✅ Fase 3 concluída — próxima: melhorias pequenas (moeda, edição com imagem) e depois a Fase 4 (mobile).
# Wishlist App

Aplicação pessoal para gerir uma wishlist de objetos, viagens e outros interesses, com controlo de orçamento e (mais tarde) extração automática de dados a partir de um link.

## Objetivo

Guardar tudo o que quero comprar/fazer num só sítio, acompanhar quanto já tenho poupado para cada coisa, e no futuro conseguir colar um link de uma loja/site e a app extrair automaticamente o nome, preço e imagem do produto.

## Roteiro

- [ ] **Fase 1 — MVP local:** base de dados + site simples onde adiciono itens manualmente
- [ ] **Fase 2 — Orçamento:** medidor de dinheiro, progresso de poupança por item, prioridades
- [ ] **Fase 3 — Parsing de links:** dado um URL, extrair nome/preço/imagem automaticamente
- [ ] **Fase 4 — Mobile:** empacotar para Android e, mais tarde, iOS

*(Este projeto está a ser construído de forma incremental — cada fase só avança depois da anterior estar sólida.)*

## Stack (Fase 1)

- **Backend:** Python + Flask
- **Base de dados:** SQLite
- **Frontend:** HTML + CSS (sem frameworks JS para já)

## Estrutura do projeto

```
wishlist-app/
├── app.py              # aplicação Flask (rotas)
├── database.py         # ligação e queries à base de dados
├── schema.sql           # definição das tabelas
├── wishlist.db          # ficheiro da base de dados (gerado)
├── templates/
│   ├── index.html       # lista de itens
│   └── add.html         # formulário de adicionar item
├── static/
│   └── style.css
├── requirements.txt
└── README.md
```

## Modelo de dados

**items**

| campo       | tipo    | descrição                              |
|-------------|---------|-----------------------------------------|
| id          | INTEGER | chave primária                          |
| name        | TEXT    | nome do item                            |
| category    | TEXT    | "objeto", "viagem" ou "interesse"       |
| price       | REAL    | preço estimado                          |
| url         | TEXT    | link do produto (opcional)              |
| image_url   | TEXT    | imagem (opcional)                       |
| notes       | TEXT    | notas livres                            |
| priority    | INTEGER | usado para ordenar a wishlist           |
| created_at  | TEXT    | data de criação                         |

**savings**

| campo   | tipo    | descrição            |
|---------|---------|-----------------------|
| id      | INTEGER | chave primária        |
| amount  | REAL    | valor poupado         |
| date    | TEXT    | data                  |

## Como correr localmente

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

A app fica disponível em `http://127.0.0.1:5000`.

## Estado atual

🚧 Em desenvolvimento — Fase 1 (MVP local).

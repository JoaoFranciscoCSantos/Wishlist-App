# Wishlist App

Aplicação pessoal para gerir uma wishlist de objetos, viagens e outros interesses, com controlo de orçamento e (mais tarde) extração automática de dados a partir de um link.

## Objetivo

Guardar tudo o que quero comprar/fazer num só sítio, acompanhar quanto já tenho poupado, e no futuro conseguir colar um link de uma loja/site e a app extrair automaticamente o nome, preço e imagem do produto.

## Roteiro

- [x] **Fase 1 — MVP local:** base de dados + site simples onde adiciono itens manualmente (CRUD completo + CSS)
- [x] **Fase 2 — Orçamento:** mealheiro único (adicionar/retirar dinheiro), compra de itens a debitar do saldo, e sugestão de compra baseada em prioridade + orçamento (algoritmo de knapsack 0/1)
- [ ] **Fase 3 — Parsing de links:** dado um URL, extrair nome/preço/imagem automaticamente
- [ ] **Fase 4 — Mobile:** empacotar para Android e, mais tarde, iOS

*(Este projeto está a ser construído de forma incremental — cada fase só avança depois da anterior estar sólida.)*

## Stack

- **Backend:** Python + Flask
- **Base de dados:** SQLite
- **Frontend:** HTML + CSS (sem frameworks JS para já)

## Estrutura do projeto

```
wishlist-app/
├── app.py              # aplicação Flask (rotas)
├── database.py         # ligação e queries à base de dados
├── suggestions.py      # algoritmo de sugestão de compra (knapsack 0/1)
├── schema.sql          # definição das tabelas
├── init_db.py           # (re)cria a base de dados a partir do schema.sql
├── wishlist.db          # ficheiro da base de dados (gerado)
├── templates/
│   ├── index.html       # lista de itens
│   ├── add.html         # formulário de adicionar item
│   └── edit.html         # formulário de editar item
├── static/
│   └── style.css
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

## Funcionalidades da Fase 2

- **Sugestão de compra na página principal:** dado o saldo atual, o algoritmo de knapsack 0/1 escolhe os itens (por comprar) que maximizam a prioridade total sem ultrapassar o saldo disponível
- **Mealheiro:** um único formulário permite depositar ou retirar dinheiro (rota `/movimento`), guardando cada movimento em `movements`
- **Marcar como comprado:** cada item por comprar tem um botão que o marca como comprado, define `purchased_at` e regista automaticamente o movimento de compra (dedução do saldo)

## Estado atual

✅ Fase 2 concluída — a começar a Fase 3 (parsing automático de links).
from flask import Flask, render_template, request, redirect, url_for, flash
from database import get_db
from suggestions import sugerir_compra
import requests
from parser import extrair_produto
import sqlite3

VAZIO = {"name": None, "price": None, "currency": None, "image_url": None}

app = Flask(__name__)
app.secret_key = "algo_qualquer"

@app.route("/")
def index():
    conn = get_db()
    items = conn.execute(
        "SELECT * FROM items ORDER BY priority DESC, created_at DESC"
    ).fetchall()

    itens_por_comprar = conn.execute(
        "SELECT * FROM items WHERE purchased = 0"
    ).fetchall()
    saldo_atual = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) as saldo FROM movements"
    ).fetchone()["saldo"]

    itens_dict = [dict(item) for item in itens_por_comprar]
    prioridade_total, escolhidos = sugerir_compra(itens_dict, saldo_atual)

    conn.close()
    return render_template(
        "index.html",
        items=items,
        escolhidos=escolhidos,
        prioridade_total=prioridade_total,
        saldo=saldo_atual
    )


@app.route("/add", methods=["GET"])
def add_form():
    return render_template("add.html", produto={}, url="")

@app.route("/add", methods=["POST"])
def add_item():
    name = request.form["name"]
    category = request.form["category"]
    price = request.form.get("price") or None
    url = request.form.get("url") or None
    image_url = request.form.get("image_url") or None
    notes = request.form.get("notes") or None
    priority = request.form.get("priority", 0)

    db = get_db()
    db.execute(
        """
        INSERT INTO items (name, category, price, url, image_url, notes, priority)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (name, category, price, url, image_url, notes, priority),
    )
    db.commit()

    return redirect(url_for("index"))


@app.route("/delete/<int:item_id>", methods=["POST"])
def delete_item(item_id):
    conn = get_db()
    try:
        conn.execute("DELETE FROM items WHERE id = ?", (item_id,))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.rollback()
        flash("Não é possível apagar este item.")
    finally:
        conn.close()
    return redirect(url_for("index"))


@app.route("/edit/<int:item_id>", methods=["GET"])
def edit_form(item_id):
    conn = get_db()
    item = conn.execute(
        "SELECT * FROM items WHERE id = ?", (item_id,)
    ).fetchone()
    conn.close()
    return render_template("edit.html", item=item)


@app.route("/edit/<int:item_id>", methods=["POST"])
def edit_item(item_id):
    name = request.form["name"]
    category = request.form["category"]
    price = float(request.form["price"])
    url = request.form.get("url")
    notes = request.form.get("notes")
    priority = int(request.form.get("priority", 1))

    conn = get_db()
    conn.execute(
        "UPDATE items SET name = ?, category = ?, price = ?, url = ?, notes = ?, priority = ? WHERE id = ?",
        (name, category, price, url, notes, priority, item_id)
    )
    conn.commit()
    conn.close()
    return redirect(url_for("index"))


@app.route('/sugestao')
def sugestao():
    db = get_db()
    itens = db.execute(
        'SELECT * FROM items WHERE purchased = 0'
    ).fetchall()

    saldo_atual = db.execute(
        'SELECT COALESCE(SUM(amount), 0) as saldo FROM movements'
    ).fetchone()['saldo']

    itens_dict = [dict(item) for item in itens]
    prioridade_total, escolhidos = sugerir_compra(itens_dict, saldo_atual)
    db.close()  # <-- adicionar isto

    return render_template('sugestao.html', escolhidos=escolhidos, prioridade_total=prioridade_total, saldo=saldo_atual)


@app.route("/deposito", methods=["POST"])
def deposito():
    amount = float(request.form["amount"])
    note = request.form.get("note")

    conn = get_db()
    conn.execute(
        "INSERT INTO movements (amount, type, note) VALUES (?, ?, ?)",
        (amount, "deposit", note)
    )
    conn.commit()
    conn.close()
    return redirect(url_for("index"))


@app.route("/retirada", methods=["POST"])
def retirada():
    amount = float(request.form["amount"])
    note = request.form.get("note")

    conn = get_db()
    conn.execute(
        "INSERT INTO movements (amount, type, note) VALUES (?, ?, ?)",
        (-amount, "withdrawal", note)
    )
    conn.commit()
    conn.close()
    return redirect(url_for("index"))


@app.route("/movimento", methods=["POST"])
def movimento():
    amount = float(request.form["amount"])
    note = request.form.get("note")
    tipo = request.form["tipo"]  # 'deposit' ou 'withdrawal'

    conn = get_db()


    if tipo == "withdrawal":
        saldo_atual = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) as saldo FROM movements"
        ).fetchone()["saldo"]

        if amount > saldo_atual:
            flash("Saldo insuficiente para esta retirada.")
            conn.close()
            return redirect(url_for("index"))

        amount = -amount
    
    conn.execute(
        "INSERT INTO movements (amount, type, note) VALUES (?, ?, ?)",
        (amount, tipo, note)
    )
    conn.commit()
    conn.close()
    return redirect(url_for("index"))


@app.route("/comprar/<int:item_id>", methods=["POST"])
def comprar(item_id):
    conn = get_db()
    item = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()

    if item is None:
        conn.close()
        flash("Item não encontrado.")
        return redirect(url_for("index"))

    conn.execute(
        "UPDATE items SET purchased = 1, purchased_at = CURRENT_TIMESTAMP WHERE id = ?",
        (item_id,)
    )
    conn.execute(
        "INSERT INTO movements (amount, type, item_id) VALUES (?, ?, ?)",
        (-item["price"], "purchase", item_id)
    )
    conn.commit()
    conn.close()
    return redirect(url_for("index"))


@app.route("/analisar", methods=["POST"])
def analisar():
    url = request.form.get("url", "").strip()

    if not url:
        flash("Cola um URL para analisar.")
        return redirect(url_for("add_form"))

    try:
        produto = extrair_produto(url)
    except requests.RequestException:
        flash("Não foi possível ler esta página. Preenche os dados manualmente.")
        produto = VAZIO
    except Exception:
        flash("Erro ao analisar a página. Preenche os dados manualmente.")
        produto = VAZIO

    if produto["name"] is None and produto["price"] is None:
        flash("Não foi encontrada informação do produto. Preenche manualmente.")

    return render_template("add.html", produto=produto, url=url)


if __name__ == "__main__":
    app.run(debug=True)
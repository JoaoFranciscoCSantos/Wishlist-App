from flask import Flask, render_template, request, redirect, url_for
from database import get_db
from suggestions import sugerir_compra

app = Flask(__name__)

@app.route("/")
def index():
    conn = get_db()
    items = conn.execute(
        "SELECT * FROM items ORDER BY priority DESC, created_at DESC"
    ).fetchall()
    conn.close()
    return render_template("index.html", items=items)


@app.route("/add", methods=["GET"])
def add_form():
    return render_template("add.html")


@app.route("/add", methods=["POST"])
def add_item():
    name = request.form["name"]
    category = request.form["category"]
    price = float(request.form["price"])
    url = request.form.get("url")
    notes = request.form.get("notes")
    priority = int(request.form.get("priority", 0))

    conn = get_db()
    conn.execute(
        "INSERT INTO items (name, category, price, url, notes, priority) VALUES (?, ?, ?, ?, ?, ?)",
        (name, category, price, url, notes, priority)
    )
    conn.commit()
    conn.close()
    return redirect(url_for("index"))


@app.route("/delete/<int:item_id>", methods=["POST"])
def delete_item(item_id):
    conn = get_db()
    conn.execute("DELETE FROM items WHERE id = ?", (item_id,))
    conn.commit()
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

    # Converter rows do SQLite para dicts simples
    itens_dict = [dict(item) for item in itens]

    prioridade_total, escolhidos = sugerir_compra(itens_dict, saldo_atual)

    return render_template('sugestao.html', escolhidos=escolhidos, prioridade_total=prioridade_total, saldo=saldo_atual)


if __name__ == "__main__":
    app.run(debug=True)
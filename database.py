import sqlite3

def get_db():
    conn = sqlite3.connect("wishlist.db")
    conn.row_factory = sqlite3.Row   # permite aceder às colunas por nome, tipo linha["name"]
    return conn
import sqlite3

conn = sqlite3.connect("wishlist.db")
with open("schema.sql") as f:
    conn.executescript(f.read())
conn.close()
print("Base de dados criada com sucesso.")
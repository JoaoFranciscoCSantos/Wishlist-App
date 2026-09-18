import sqlite3

def get_db():
    conn = sqlite3.connect("wishlist.db")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
import sqlite3

conn = sqlite3.connect("wishlist.db")
conn.execute("PRAGMA foreign_keys = OFF")  # necessário durante a migração

conn.executescript("""
BEGIN TRANSACTION;

CREATE TABLE movements_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL NOT NULL,
    type TEXT NOT NULL,
    item_id INTEGER,
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE SET NULL
);

INSERT INTO movements_new (id, amount, type, item_id, note, created_at)
SELECT id, amount, type, item_id, note, created_at FROM movements;

DROP TABLE movements;

ALTER TABLE movements_new RENAME TO movements;

COMMIT;
""")

conn.close()
print("Migração concluída.")
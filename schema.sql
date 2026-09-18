CREATE TABLE IF NOT EXISTS items(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    price REAL,
    url TEXT,
    image_url TEXT,
    notes TEXT,
    priority INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    purchased INTEGER DEFAULT 0,
    purchased_at TIMESTAMP
);

CREATE TABLE movements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL NOT NULL,        -- positivo = depósito, negativo = retirada/compra
    type TEXT NOT NULL,          -- 'deposit', 'withdrawal', 'purchase'
    item_id INTEGER,             -- só preenchido quando type = 'purchase'
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (item_id) REFERENCES items(id)
);
import sqlite3

def init_db():
    conn = sqlite3.connect("farmlink.db")
    cursor = conn.cursor()

    conn.execute("PRAGMA foreign_keys = ON")

  
    # USERS TABLE

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('Farmer', 'Buyer'))
    )
    """)


    # INVENTORY TABLE

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        farmer_id INTEGER,
        crop_name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        price REAL,
        status TEXT DEFAULT 'Stored',
        FOREIGN KEY (farmer_id) REFERENCES users(id)
    )
    """)


    # TRANSACTIONS TABLE

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        buyer_id INTEGER,
        crop_id INTEGER,
        quantity INTEGER,
        total_price REAL,
        FOREIGN KEY (buyer_id) REFERENCES users(id),
        FOREIGN KEY (crop_id) REFERENCES inventory(id)
    )
    """)
    
    conn.commit()
    conn.close()

import sqlite3

def init_db():
    conn = sqlite3.connect("prospects.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS prospects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER,
        username TEXT,
        fullname TEXT,
        level TEXT,
        pack TEXT,
        goal TEXT,
        score INTEGER DEFAULT 0,
        status TEXT DEFAULT 'Nouveau'
    )
    """)
    conn.commit()
    return conn

conn = init_db()

def save_prospect(telegram_id, username, fullname, level, pack, goal, score):
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO prospects (telegram_id, username, fullname, level, pack, goal, score)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (telegram_id, username, fullname, level, pack, goal, score))
    conn.commit()

def get_all_prospects():
    cursor = conn.cursor()
    cursor.execute("SELECT id, fullname, pack, score, status FROM prospects ORDER BY score DESC")
    return cursor.fetchall()
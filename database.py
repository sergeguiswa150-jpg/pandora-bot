import sqlite3

conn = sqlite3.connect(
    "prospects.db",
    check_same_thread=False
)

conn.row_factory = sqlite3.Row

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS prospects(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER,
    username TEXT,
    fullname TEXT,
    category TEXT,
    level TEXT,
    pack TEXT,
    capital TEXT,
    message TEXT,
    score INTEGER DEFAULT 0,
    status TEXT DEFAULT 'new'
)
""")

conn.commit()


def add_prospect(
    telegram_id,
    username,
    fullname,
    category,
    level,
    pack,
    capital,
    message,
    score
):

    cursor.execute("""
    INSERT INTO prospects(
        telegram_id,
        username,
        fullname,
        category,
        level,
        pack,
        capital,
        message,
        score
    )
    VALUES(?,?,?,?,?,?,?,?,?)
    """,(
        telegram_id,
        username,
        fullname,
        category,
        level,
        pack,
        capital,
        message,
        score
    ))

    conn.commit()


def get_prospects():

    cursor.execute("""
    SELECT * FROM prospects
    ORDER BY score DESC,id DESC
    """)

    return cursor.fetchall()


def update_status(
    telegram_id,
    status
):

    cursor.execute("""
    UPDATE prospects
    SET status=?
    WHERE telegram_id=?
    """,(status,telegram_id))

    conn.commit()

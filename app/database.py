import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database.db"


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')

    # Create progress table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            cookies INTEGER DEFAULT 0,
            totalCookies INTEGER DEFAULT 0,
            cps REAL DEFAULT 0.0,
            cursor_count INTEGER DEFAULT 0,
            grandma_count INTEGER DEFAULT 0,
            factory_count INTEGER DEFAULT 0
        )
    ''')

    conn.commit()
    conn.close()


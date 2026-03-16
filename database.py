import sqlite3
from datetime import datetime

DB_PATH = "database.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        username   TEXT UNIQUE NOT NULL,
        password   TEXT NOT NULL,
        api_key    TEXT NOT NULL,
        is_admin   INTEGER DEFAULT 0,
        created_at TEXT NOT NULL,
        last_login TEXT
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS apis (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        name          TEXT NOT NULL,
        description   TEXT NOT NULL,
        endpoint      TEXT NOT NULL,
        category      TEXT DEFAULT 'other',
        owner         TEXT NOT NULL,
        rating        REAL DEFAULT 0,
        rating_count  INTEGER DEFAULT 0,
        views         INTEGER DEFAULT 0,
        created_at    TEXT NOT NULL
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS comments (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        api_id     INTEGER NOT NULL,
        username   TEXT NOT NULL,
        body       TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(api_id) REFERENCES apis(id) ON DELETE CASCADE
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS api_logs (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id    INTEGER,
        api_key    TEXT,
        endpoint   TEXT,
        status     INTEGER,
        ip         TEXT,
        created_at TEXT NOT NULL
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS rate_limits (
        api_key      TEXT PRIMARY KEY,
        requests     INTEGER DEFAULT 0,
        window_start TEXT NOT NULL
    )""")

    # Safe migrations for existing DBs
    migrations = [
        ("users", "created_at TEXT NOT NULL DEFAULT ''"),
        ("users", "last_login TEXT"),
        ("users", "is_admin INTEGER DEFAULT 0"),
        ("apis",  "category TEXT DEFAULT 'other'"),
        ("apis",  "created_at TEXT NOT NULL DEFAULT ''"),
    ]
    for table, col_def in migrations:
        try:
            c.execute(f"ALTER TABLE {table} ADD COLUMN {col_def}") #This adds the missing column safely.
        except Exception:
            pass

    conn.commit()
    conn.close()
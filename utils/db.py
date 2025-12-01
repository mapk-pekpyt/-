# utils/db.py
import sqlite3
from config import DB

def db_conn():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def db_execute(query, params=(), fetch=False):
    conn = db_conn()
    cur = conn.cursor()
    cur.execute(query, params)
    result = cur.fetchall() if fetch else None
    conn.commit()
    conn.close()
    return result

def init_db():
    tables = [
        """CREATE TABLE IF NOT EXISTS boobs (chat_id TEXT, user_id TEXT, size INTEGER, last_date TEXT, PRIMARY KEY(chat_id, user_id))""",
        """CREATE TABLE IF NOT EXISTS klitor (chat_id TEXT, user_id TEXT, size_mm INTEGER, last_date TEXT, PRIMARY KEY(chat_id, user_id))""",
        """CREATE TABLE IF NOT EXISTS hui (chat_id TEXT, user_id TEXT, size_cm INTEGER, last_date TEXT, PRIMARY KEY(chat_id, user_id))""",
        """CREATE TABLE IF NOT EXISTS whoami (chat_id TEXT, user_id TEXT, choice TEXT, date TEXT, PRIMARY KEY(chat_id, user_id))""",
        """CREATE TABLE IF NOT EXISTS names (chat_id TEXT, user_id TEXT, display_name TEXT, PRIMARY KEY(chat_id, user_id))""",
        """CREATE TABLE IF NOT EXISTS birthdays (chat_id TEXT, user_id TEXT, date TEXT, PRIMARY KEY(chat_id, user_id))""",
    ]
    for q in tables:
        db_execute(q)
# utils/db.py
import sqlite3
import os
from config import DB_PATH

def db_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def db_execute(query, params=(), fetch=False):
    conn = db_conn()
    cur = conn.cursor()
    cur.execute(query, params)
    data = cur.fetchall() if fetch else None
    conn.commit()
    conn.close()
    return data

# Инициализация всех нужных таблиц (взято из твоего текущего кода)
def init_db():
    db_execute("""CREATE TABLE IF NOT EXISTS boobs (
        chat_id TEXT,
        user_id TEXT,
        size INTEGER,
        last_date TEXT,
        PRIMARY KEY(chat_id, user_id)
    )""")
    db_execute("""CREATE TABLE IF NOT EXISTS klitor (
        chat_id TEXT,
        user_id TEXT,
        size_mm INTEGER,
        last_date TEXT,
        PRIMARY KEY(chat_id, user_id)
    )""")
    db_execute("""CREATE TABLE IF NOT EXISTS hui (
        chat_id TEXT,
        user_id TEXT,
        size_cm INTEGER,
        last_date TEXT,
        PRIMARY KEY(chat_id, user_id)
    )""")
    db_execute("""CREATE TABLE IF NOT EXISTS whoami (
        chat_id TEXT,
        user_id TEXT,
        choice TEXT,
        date TEXT,
        PRIMARY KEY(chat_id, user_id)
    )""")
    db_execute("""CREATE TABLE IF NOT EXISTS names (
        chat_id TEXT,
        user_id TEXT,
        display_name TEXT,
        PRIMARY KEY(chat_id, user_id)
    )""")
    db_execute("""CREATE TABLE IF NOT EXISTS birthdays (
        chat_id TEXT,
        user_id TEXT,
        date TEXT,
        PRIMARY KEY(chat_id, user_id)
    )""")

# Пакет утилит, которые плагины будут получать
def get_db_utils():
    return {
        "db_execute": db_execute,
        "db_conn": db_conn,
        "init_db": init_db
    }
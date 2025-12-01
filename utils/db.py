import sqlite3

DB = "boobs.db"

def db_conn():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def db_execute(q, p=(), f=False):
    c = db_conn()
    cur = c.cursor()
    cur.execute(q, p)
    res = cur.fetchall() if f else None
    c.commit()
    c.close()
    return res

def init_db():
    t = [
        "CREATE TABLE IF NOT EXISTS boobs (chat_id TEXT,user_id TEXT,size INTEGER,last_date TEXT,PRIMARY KEY(chat_id,user_id))",
        "CREATE TABLE IF NOT EXISTS klitor (chat_id TEXT,user_id TEXT,size_mm INTEGER,last_date TEXT,PRIMARY KEY(chat_id,user_id))",
        "CREATE TABLE IF NOT EXISTS hui (chat_id TEXT,user_id TEXT,size_cm INTEGER,last_date TEXT,PRIMARY KEY(chat_id,user_id))",
        "CREATE TABLE IF NOT EXISTS whoami (chat_id TEXT,user_id TEXT,choice TEXT,date TEXT,PRIMARY KEY(chat_id,user_id))",
        "CREATE TABLE IF NOT EXISTS names (chat_id TEXT,user_id TEXT,display_name TEXT,PRIMARY KEY(chat_id,user_id))",
        "CREATE TABLE IF NOT EXISTS birthdays (chat_id TEXT,user_id TEXT,date TEXT,PRIMARY KEY(chat_id,user_id))"
    ]
    for x in t: 
        db_execute(x)
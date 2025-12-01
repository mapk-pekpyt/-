import datetime
import random
from utils.db import db_execute
from config import bot

def get_display_name(cid, uid):
    row = db_execute(
        "SELECT display_name FROM names WHERE chat_id=? AND user_id=?",
        (str(cid), str(uid)), True
    )
    if row:
        return row[0]["display_name"]
    try:
        user = bot.get_chat_member(cid, uid).user
        name = user.first_name or ""
        if user.last_name:
            name += " " + user.last_name
        return name.strip() or "Аноним"
    except:
        return "Аноним"

def change_size(table, cid, uid, delta_range=(-10,10)):
    today = datetime.date.today().isoformat()
    col = {"boobs":"size", "klitor":"size_mm", "hui":"size_cm"}[table]
    row = db_execute(
        f"SELECT {col}, last_date FROM {table} WHERE chat_id=? AND user_id=?",
        (str(cid), str(uid)), True
    )
    if row and row[0]["last_date"] == today:
        return 0, row[0][col]

    current = row[0][col] if row else 0
    delta = random.randint(*delta_range)
    if current + delta < 0:
        delta = -current
    new_size = current + delta

    db_execute(
        f"INSERT OR REPLACE INTO {table}(chat_id,user_id,{col},last_date) VALUES(?,?,?,?)",
        (str(cid), str(uid), new_size, today)
    )
    return delta, new_size
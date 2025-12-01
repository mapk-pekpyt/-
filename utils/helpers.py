# utils/helpers.py
from config import bot
from utils.db import db_execute

def get_display_name(chat_id, user_id):
    row = db_execute("SELECT display_name FROM names WHERE chat_id=? AND user_id=?", (str(chat_id), str(user_id)), fetch=True)
    if row:
        return row[0]["display_name"]
    try:
        member = bot.get_chat_member(chat_id, user_id)
        user = member.user
        name = user.first_name or ""
        if user.last_name:
            name += " " + user.last_name
        return name.strip() or "Пользователь"
    except:
        return "Пользователь"

def change_size(table, chat_id, user_id, delta_range=(-10, 10)):
    import datetime, random
    today = datetime.date.today().isoformat()
    chat, user = str(chat_id), str(user_id)

    size_col = {"boobs": "size", "klitor": "size_mm", "hui": "size_cm"}[table]
    row = db_execute(f"SELECT {size_col}, last_date FROM {table} WHERE chat_id=? AND user_id=?", (chat, user), fetch=True)

    if row and row[0]["last_date"] == today:
        return 0, row[0][size_col]

    current = row[0][size_col] if row else 0
    delta = random.randint(*delta_range)
    if current + delta < 0:
        delta = -current
    new_size = current + delta

    db_execute(f"INSERT OR REPLACE INTO {table} (chat_id, user_id, {size_col}, last_date) VALUES (?, ?, ?, ?)",
               (chat, user, new_size, today))
    return delta, new_size
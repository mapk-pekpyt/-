# main.py — исправленная версия (pyTelegramBotAPI)
import os
import sqlite3
import telebot
import random
import datetime
import re

TOKEN = os.environ.get("BOT_TOKEN", "YOUR_TOKEN_HERE")
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

DB = "boobs.db"

def db_conn():
    conn = sqlite3.connect(DB)
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

# Init tables
db_execute("""CREATE TABLE IF NOT EXISTS boobs (
    chat_id TEXT,
    user_id TEXT,
    size INTEGER,
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

ADMIN_USERNAME = "Sugar_Daddy_rip"
PROVIDER_TOKEN = ""  # если будешь подключать Stars

# --- склонение: возвращает только слово-окончание фразы, без числа
def declension(n: int) -> str:
    # Возвращает правильное окончание: "размер груди", "размера груди", "размеров груди"
    if n % 10 == 1 and n % 100 != 11:
        return "размер груди"
    elif 2 <= n % 10 <= 4 and not (12 <= n % 100 <= 14):
        return "размера груди"
    else:
        return "размеров груди"

def get_stored_name(chat_id, user_id):
    row = db_execute("SELECT display_name FROM names WHERE chat_id=? AND user_id=?", (str(chat_id), str(user_id)), fetch=True)
    if row:
        return row[0]["display_name"]
    return None

def get_user_name_fallback(chat_id, user_id):
    # Пытаемся получить имя через API (если бот имеет доступ), иначе вернём "Пользователь"
    try:
        member = bot.get_chat_member(chat_id, user_id)
        user = member.user
        # используем first_name + (last_name если есть)
        if getattr(user, "last_name", None):
            return f"{user.first_name} {user.last_name}"
        return user.first_name or f"Пользователь"
    except Exception:
        return "Пользователь"

def get_display_name(chat_id, user_id):
    name = get_stored_name(chat_id, user_id)
    if name:
        return name
    return get_user_name_fallback(chat_id, user_id)

# core logic
def change_boobs(chat_id, user_id):
    today = datetime.date.today().isoformat()
    chat = str(chat_id); user = str(user_id)
    row = db_execute("SELECT size,last_date FROM boobs WHERE chat_id=? AND user_id=?", (chat, user), fetch=True)
    if row:
        size = row[0]["size"]
        last = row[0]["last_date"]
    else:
        size = 0
        last = None

    if last == today:
        return 0, size

    delta = random.randint(-10, 10)
    if size + delta < 0:
        delta = -size
    new_size = size + delta

    db_execute("INSERT OR REPLACE INTO boobs(chat_id,user_id,size,last_date) VALUES (?,?,?,?)",
               (chat, user, new_size, today))
    return delta, new_size

def whoami(chat_id, user_id):
    today = datetime.date.today().isoformat()
    chat = str(chat_id); user = str(user_id)
    row = db_execute("SELECT choice,date FROM whoami WHERE chat_id=? AND user_id=?", (chat, user), fetch=True)
    if row and row[0]["date"] == today:
        return row[0]["choice"]
    choice = random.choice(["ты лох 😏", "удивительно, но сегодня ты не лох 🎉"])
    db_execute("INSERT OR REPLACE INTO whoami(chat_id,user_id,choice,date) VALUES (?,?,?,?)",
               (chat, user, choice, today))
    return choice

# --- Commands (English) with Russian messages
@bot.message_handler(commands=['commands'])
def cmd_commands(m):
    bot.reply_to(m,
                 "Привет! Я бот с грудями 😏\n\n"
                 "Команды:\n"
                 "/sisi — получить рост груди на сегодня 🍒\n"
                 "/my — показать свой размер груди 🍒\n"
                 "/buy_boobs — купить +1 груди за 5 ⭐ 🎉\n"
                 "/top — топ участников по размеру груди 😎\n"
                 "/name <имя> — установить своё отображаемое имя 😏\n"
                 "/dr <дд.мм.гггг> — записать день рождения 🎂\n"
                 "/dr all — список ДР в чате 🎂\n"
                 "/kto — узнать, кто ты сегодня (1 раз в день) 😉")

@bot.message_handler(commands=['sisi'])
def cmd_sisi(m):
    chat_id = m.chat.id; user_id = m.from_user.id
    name = get_display_name(chat_id, user_id)
    delta, new_size = change_boobs(chat_id, user_id)
    if delta == 0:
        bot.reply_to(m, f"Ой, а ты уже пробовал сегодня 😅\nТвой текущий размер груди равен <b>{new_size}</b> {declension(new_size)} 🍒")
    else:
        # sign display: +6 or -3
        sign = f"{delta:+d}"
        bot.reply_to(m, f"🍒 {name}, твой размер груди вырос на <b>{sign}</b>, теперь твой размер груди равен <b>{new_size}</b> {declension(new_size)} 🍒")

@bot.message_handler(commands=['my'])
def cmd_my(m):
    chat_id = str(m.chat.id); user = str(m.from_user.id)
    row = db_execute("SELECT size FROM boobs WHERE chat_id=? AND user_id=?", (chat_id, user), fetch=True)
    size = row[0]["size"] if row else 0
    name = get_display_name(m.chat.id, m.from_user.id)
    bot.reply_to(m, f"✨ {name}, твой текущий размер груди: <b>{size}</b> {declension(size)} 🍒")

@bot.message_handler(commands=['top'])
def cmd_top(m):
    chat_id = str(m.chat.id)
    rows = db_execute("SELECT user_id,size FROM boobs WHERE chat_id=? ORDER BY size DESC LIMIT 10", (chat_id,), fetch=True)
    if not rows:
        bot.reply_to(m, "Пусто 😅")
        return
    text = "🏆 <b>ТОП груди</b>:\n\n"
    for i, r in enumerate(rows, start=1):
        uid = r["user_id"]; size = r["size"]
        name = get_display_name(chat_id, uid)
        text += f"{i}. {name} — <b>{size}</b> {declension(size)} 🍒\n"
    bot.reply_to(m, text)

@bot.message_handler(commands=['name'])
def cmd_name(m):
    parts = m.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(m, "Используй: /name ТвоёИмя")
        return
    chat_id = str(m.chat.id); user_id = str(m.from_user.id)
    name_text = parts[1].strip()
    db_execute("INSERT OR REPLACE INTO names(chat_id,user_id,display_name) VALUES (?,?,?)",
               (chat_id, user_id, name_text))
    bot.reply_to(m, f"🎉 Ваше имя изменено на '{name_text}'")

@bot.message_handler(commands=['dr'])
def cmd_dr(m):
    parts = m.text.split()
    chat_id = str(m.chat.id); user_id = str(m.from_user.id)
    if len(parts) == 1:
        row = db_execute("SELECT date FROM birthdays WHERE chat_id=? AND user_id=?", (chat_id, user_id), fetch=True)
        if row:
            bot.reply_to(m, f"🎂 Твой день рождения: {row[0]['date']}")
        else:
            bot.reply_to(m, "🎂 Ты ещё не указал день рождения")
        return
    if parts[1].lower() == "all":
        rows = db_execute("SELECT user_id,date FROM birthdays WHERE chat_id=?", (chat_id,), fetch=True)
        if not rows:
            bot.reply_to(m, "🎂 Нет дней рождения 😅")
            return
        text = "🎂 Дни рождения чата:\n"
        for r in rows:
            uid = r["user_id"]; d = r["date"]
            name = get_display_name(chat_id, uid)
            text += f"{name} — {d}\n"
        bot.reply_to(m, text)
        return
    date_text = parts[1]
    if not re.match(r"\d{2}\.\d{2}\.\d{4}$", date_text):
        bot.reply_to(m, "Используй формат: /dr дд.мм.гггг")
        return
    db_execute("INSERT OR REPLACE INTO birthdays(chat_id,user_id,date) VALUES (?,?,?)",
               (chat_id, user_id, date_text))
    bot.reply_to(m, f"🎂 День рождения сохранён: {date_text}")

@bot.message_handler(commands=['kto'])
def cmd_kto(m):
    chat_id = str(m.chat.id); user_id = str(m.from_user.id)
    res = whoami(chat_id, user_id)
    bot.reply_to(m, res)

# buy via Telegram Stars (provider token must be set & available in your region)
@bot.message_handler(commands=['buy_boobs'])
def cmd_buy(m):
    chat = m.chat.id; uid = m.from_user.id
    price = 5
    payload = f"buy_boobs_{chat}_{uid}"
    from telebot.types import LabeledPrice
    prices = [LabeledPrice(label="1 единица груди", amount=price)]
    bot.send_invoice(m.chat.id,
                     title="Покупка груди",
                     description="Покупка +1 груди за 5 ⭐",
                     invoice_payload=payload,
                     currency="XTR",
                     prices=prices,
                     provider_token=PROVIDER_TOKEN,
                     start_parameter="buyboobs")

@bot.pre_checkout_query_handler(func=lambda q: True)
def precheckout(q):
    bot.answer_pre_checkout_query(q.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def got_payment(m):
    payload = m.successful_payment.invoice_payload
    if payload.startswith("buy_boobs_"):
        _, chat, uid = payload.split("_")
        row = db_execute("SELECT size FROM boobs WHERE chat_id=? AND user_id=?", (str(chat), str(uid)), fetch=True)
        size = row[0]["size"] if row else 0
        size += 1
        db_execute("INSERT OR REPLACE INTO boobs(chat_id,user_id,size,last_date) VALUES (?,?,?,?)",
                   (str(chat), str(uid), size, datetime.date.today().isoformat()))
        name = get_display_name(chat, uid)
        bot.send_message(int(chat), f"🎉 {name} купил(а) +1 груди!\nНовый размер: <b>{size}</b> {declension(size)} 🍒")

# catch plain messages (works in groups and PM)
@bot.message_handler(func=lambda m: True, content_types=['text'])
def general_handler(m):
    text = (m.text or "").lower()
    chat_id = m.chat.id
    user_id = m.from_user.id

    if text.startswith("/sisi") or "sisi" in text or "сиськи" in text:
        # reuse same logic as command
        name = get_display_name(chat_id, user_id)
        delta, new_size = change_boobs(chat_id, user_id)
        if delta == 0:
            bot.reply_to(m, f"Ой, а ты уже пробовал сегодня 😅\nТвой текущий размер груди равен <b>{new_size}</b> {declension(new_size)} 🍒")
        else:
            sign = f"{delta:+d}"
            bot.reply_to(m, f"🍒 {name}, твой размер груди вырос на <b>{sign}</b>, теперь твой размер груди равен <b>{new_size}</b> {declension(new_size)} 🍒")
        return

    if text.startswith("/kto") or "kto" in text or "кто же я" in text:
        res = whoami(str(chat_id), str(user_id))
        bot.reply_to(m, res)
        return

if __name__ == "__main__":
    bot.infinity_polling(skip_pending=True)
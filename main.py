import sqlite3
import telebot
from telebot.types import LabeledPrice
import random
import datetime
import re
import os

TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# ==========================
# БАЗА ДАННЫХ
# ==========================
def db_execute(query, params=(), fetch=False):
    conn = sqlite3.connect("boobs.db")
    cur = conn.cursor()
    cur.execute(query, params)
    data = cur.fetchall() if fetch else None
    conn.commit()
    conn.close()
    return data

# Таблица размера груди
db_execute("""
CREATE TABLE IF NOT EXISTS boobs (
    chat_id TEXT,
    user_id TEXT,
    size INTEGER,
    last_date TEXT,
    PRIMARY KEY(chat_id, user_id)
)
""")

# Таблица ДР
db_execute("""
CREATE TABLE IF NOT EXISTS birthdays (
    chat_id TEXT,
    user_id TEXT,
    date TEXT,
    PRIMARY KEY(chat_id, user_id)
)
""")

# ==========================
# ПОМОЩНИКИ
# ==========================
def has_permission(user_id):
    return str(user_id) in ["5356165089", "6219863577", "8030707743"]

def change_boobs(chat_id, user_id):
    chat_id = str(chat_id)
    user_id = str(user_id)
    
    row = db_execute("SELECT size FROM boobs WHERE chat_id=? AND user_id=?", (chat_id, user_id), fetch=True)
    size = row[0][0] if row else 0
    
    delta = random.randint(-10, 10)
    if size + delta < 0:
        delta = -size
    new_size = size + delta
    
    db_execute("INSERT OR REPLACE INTO boobs(chat_id,user_id,size,last_date) VALUES (?,?,?,?)",
               (chat_id, user_id, new_size, datetime.date.today().isoformat()))
    
    return new_size

# ==========================
# СТАРТОВЫЕ КОМАНДЫ
# ==========================
@bot.message_handler(commands=['start'])
def cmd_start(m):
    bot.reply_to(m, "Привет! Я бот с грудями 😏\n\n"
                    "Команды и функции:\n"
                    "сиськи — выдать размер груди на сегодня\n"
                    "/my — показать свой размер груди\n"
                    "/buy_boobs — купить +1 груди за 5 ⭐\n"
                    "/top — топ участников по размеру груди\n"
                    "/add — добавить размер пользователю (только админ)\n"
                    "/dr дд.мм.гггг — записать свой день рождения\n"
                    "/dr — показать свой день рождения\n"
                    "/dr all — список всех ДР в чате\n"
                    "кто же я — бот рандомно отвечает, лох ты или не лох 😉")

# ==========================
# СЛОВО "СИСКИ"
# ==========================
@bot.message_handler(func=lambda m: "сиськи" in m.text.lower())
def boobs_handler(m):
    new_size = change_boobs(m.chat.id, m.from_user.id)
    bot.reply_to(m, f"Твой размер груди сегодня: <b>{new_size}</b> 🍒")

# ==========================
# КТО ЖЕ Я
# ==========================
@bot.message_handler(func=lambda m: "кто же я" in m.text.lower())
def whoami_handler(m):
    answer = random.choice(["ты лох", "удивительно, но сегодня ты не лох"])
    bot.reply_to(m, answer)

# ==========================
# МОЙ РАЗМЕР
# ==========================
@bot.message_handler(commands=['my'])
def cmd_my(m):
    chat_id = str(m.chat.id)
    user_id = str(m.from_user.id)

    row = db_execute("SELECT size FROM boobs WHERE chat_id=? AND user_id=?", (chat_id, user_id), fetch=True)
    if not row:
        bot.reply_to(m, "У тебя ещё нет размера 😅 Напиши 'сиськи' чтобы получить.")
        return

    bot.reply_to(m, f"✨ Твой размер груди: <b>{row[0][0]}</b>")

# ==========================
# ТОП
# ==========================
@bot.message_handler(commands=['top'])
def cmd_top(m):
    chat_id = str(m.chat.id)
    rows = db_execute("SELECT user_id,size FROM boobs WHERE chat_id=? ORDER BY size DESC LIMIT 10", (chat_id,), fetch=True)
    if not rows:
        bot.reply_to(m, "Нет данных 😅")
        return
    text = "🏆 <b>ТОП груди</b>:\n\n"
    for i, (uid, size) in enumerate(rows, start=1):
        text += f"{i}. <a href='tg://user?id={uid}'>Пользователь</a> — <b>{size}</b>\n"
    bot.reply_to(m, text)

# ==========================
# ДОБАВИТЬ РАЗМЕР (АДМИН)
# ==========================
@bot.message_handler(commands=['add'])
def cmd_add(m):
    if not has_permission(m.from_user.id):
        bot.reply_to(m, "Нет доступа ❌")
        return
    cmd = m.text.split()
    if len(cmd) != 3:
        bot.reply_to(m, "Используй: /add @user 5")
        return
    target = cmd[1]
    add = int(cmd[2])
    if not re.match(r"^@[\w_]+$", target):
        bot.reply_to(m, "Неверный @username")
        return
    chat_id = str(m.chat.id)
    uid = None
    # ищем user_id по username
    try:
        members = bot.get_chat_administrators(m.chat.id)
    except:
        bot.reply_to(m, "Ошибка доступа к списку участников")
        return
    for adm in members:
        if adm.user.username and adm.user.username.lower() == target[1:].lower():
            uid = adm.user.id
            break
    if not uid:
        bot.reply_to(m, "Пользователь не найден")
        return
    row = db_execute("SELECT size FROM boobs WHERE chat_id=? AND user_id=?", (chat_id, uid), fetch=True)
    size = row[0][0] if row else 0
    size += add
    db_execute("INSERT OR REPLACE INTO boobs(chat_id,user_id,size,last_date) VALUES (?,?,?,?)",
               (chat_id, uid, size, ""))
    bot.reply_to(m, f"Готово! @{target[1:]} теперь имеет размер {size} 🍒")

# ==========================
# ДР
# ==========================
@bot.message_handler(commands=['dr'])
def birthdays(m):
    chat_id = str(m.chat.id)
    user_id = str(m.from_user.id)
    cmd = m.text.split()
    
    if len(cmd) == 1:
        row = db_execute("SELECT date FROM birthdays WHERE chat_id=? AND user_id=?", (chat_id, user_id), fetch=True)
        if row:
            bot.reply_to(m, f"Твой день рождения: {row[0][0]}")
        else:
            bot.reply_to(m, "Ты ещё не указал день рождения")
        return

    if cmd[1].lower() == "all":
        rows = db_execute("SELECT user_id,date FROM birthdays WHERE chat_id=?", (chat_id,), fetch=True)
        if not rows:
            bot.reply_to(m, "Нет дней рождения 😅")
            return
        text = "🎂 Дни рождения чата:\n"
        for uid, date in rows:
            text += f"<a href='tg://user?id={uid}'>Пользователь</a> — {date}\n"
        bot.reply_to(m, text)
        return

    date_text = cmd[1]
    if not re.match(r"\d{2}\.\d{2}\.\d{4}", date_text):
        bot.reply_to(m, "Используй формат: /dr дд.мм.гггг")
        return

    db_execute("INSERT OR REPLACE INTO birthdays(chat_id,user_id,date) VALUES (?,?,?)",
               (chat_id, user_id, date_text))
    bot.reply_to(m, f"День рождения сохранён: {date_text}")

# ==========================
# ПОКУПКА +1 ГРУДИ ЗА 5 ⭐
# ==========================
@bot.message_handler(commands=['buy_boobs'])
def cmd_buy(m):
    chat_id = str(m.chat.id)
    uid = str(m.from_user.id)
    star_price = 5  # 5 ⭐
    payload = f"buy_boobs_{chat_id}_{uid}"
    prices = [LabeledPrice(label="1 единица груди", amount=star_price)]
    bot.send_invoice(
        chat_id=m.chat.id,
        title="Покупка груди",
        description="Покупка +1 груди за 5 ⭐",
        invoice_payload=payload,
        currency="XTR",
        prices=prices,
        provider_token="",  # для Telegram Stars не нужен
        start_parameter="buyboobs"
    )

@bot.pre_checkout_query_handler(func=lambda q: True)
def checkout(q):
    bot.answer_pre_checkout_query(q.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def payment_success(m):
    payload = m.successful_payment.invoice_payload
    if payload.startswith("buy_boobs_"):
        _, chat_id, uid = payload.split("_")
        row = db_execute("SELECT size FROM boobs WHERE chat_id=? AND user_id=?", (chat_id, uid), fetch=True)
        size = row[0][0] if row else 0
        size += 1
        db_execute("INSERT OR REPLACE INTO boobs(chat_id,user_id,size,last_date) VALUES (?,?,?,?)",
                   (chat_id, uid, size, ""))
        bot.send_message(int(chat_id), f"🎉 <a href='tg://user?id={uid}'>Пользователь</a> купил +1 груди!\n"
                                       f"Новый размер: <b>{size}</b> 🍒")

# ==========================
# ПУСК
# ==========================
if __name__ == "__main__":
    bot.infinity_polling(skip_pending=True)
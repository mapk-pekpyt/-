import sqlite3
import telebot
from telebot.types import LabeledPrice
import random
import datetime
import re
import os

TOKEN = os.environ.get("BOT_TOKEN")  # или вставь свой токен
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

# Таблицы
db_execute("""CREATE TABLE IF NOT EXISTS boobs (
    chat_id TEXT,
    user_id TEXT,
    size INTEGER,
    last_date TEXT,
    PRIMARY KEY(chat_id, user_id)
)""")

db_execute("""CREATE TABLE IF NOT EXISTS birthdays (
    chat_id TEXT,
    user_id TEXT,
    date TEXT,
    PRIMARY KEY(chat_id, user_id)
)""")

db_execute("""CREATE TABLE IF NOT EXISTS names (
    chat_id TEXT,
    user_id TEXT,
    display_name TEXT,
    PRIMARY KEY(chat_id, user_id)
)""")

db_execute("""CREATE TABLE IF NOT EXISTS whoami (
    chat_id TEXT,
    user_id TEXT,
    choice TEXT,
    date TEXT,
    PRIMARY KEY(chat_id, user_id)
)""")

# ==========================
# ПОМОЩНИКИ
# ==========================
ADMIN_USERNAME = "Sugar_Daddy_rip"

def is_admin(user):
    return user.username == ADMIN_USERNAME

def get_display_name(chat_id, user_id):
    row = db_execute("SELECT display_name FROM names WHERE chat_id=? AND user_id=?", (chat_id, user_id), fetch=True)
    return row[0][0] if row else None

def change_boobs(chat_id, user_id):
    today = datetime.date.today().isoformat()
    chat_id, user_id = str(chat_id), str(user_id)
    row = db_execute("SELECT size,last_date FROM boobs WHERE chat_id=? AND user_id=?", (chat_id, user_id), fetch=True)
    size, last = (row[0][0], row[0][1]) if row else (0, None)
    if last == today:
        return 0, size
    delta = random.randint(1,10)  # рост груди один раз в день
    new_size = size + delta
    db_execute("INSERT OR REPLACE INTO boobs(chat_id,user_id,size,last_date) VALUES (?,?,?,?)",
               (chat_id,user_id,new_size,today))
    return delta, new_size

def whoami(chat_id, user_id):
    today = datetime.date.today().isoformat()
    chat_id, user_id = str(chat_id), str(user_id)
    row = db_execute("SELECT choice,date FROM whoami WHERE chat_id=? AND user_id=?", (chat_id,user_id), fetch=True)
    if row and row[0][1] == today:
        return row[0][0]
    choice = random.choice(["ты лох 😏","удивительно, но сегодня ты не лох 🎉"])
    db_execute("INSERT OR REPLACE INTO whoami(chat_id,user_id,choice,date) VALUES (?,?,?,?)",
               (chat_id,user_id,choice,today))
    return choice

def boob_word(n):
    if n % 10 == 1 and n % 100 != 11:
        return "грудь"
    elif 2 <= n % 10 <= 4 and not (12 <= n % 100 <= 14):
        return "груди"
    else:
        return "грудей"

# ==========================
# КОМАНДЫ
# ==========================
@bot.message_handler(commands=['komands'])
def cmd_komands(m):
    bot.reply_to(m, "Привет! Я бот с грудями 😏\n\n"
                    "Команды и функции:\n"
                    "сиськи — получить рост груди на сегодня 🍒\n"
                    "/my — показать свой размер груди 🍒\n"
                    "/buy_boobs — купить +1 груди за 5 ⭐ 🎉\n"
                    "/top — топ участников по размеру груди 😎\n"
                    "/имя <имя> — установить своё имя для отображения 😏\n"
                    "/dr дд.мм.гггг — записать свой день рождения 🎂\n"
                    "/dr — показать свой день рождения 🎂\n"
                    "/dr all — список всех ДР в чате 🎂\n"
                    "кто же я — бот рандомно отвечает один раз в день 😉")

@bot.message_handler(commands=['my'])
def cmd_my(m):
    chat_id, user_id = str(m.chat.id), str(m.from_user.id)
    row = db_execute("SELECT size FROM boobs WHERE chat_id=? AND user_id=?", (chat_id,user_id), fetch=True)
    name = get_display_name(chat_id, user_id) or m.from_user.first_name
    if not row:
        bot.reply_to(m, f"🍒 {name}, у тебя ещё нет размера 😅 Напиши 'сиськи' чтобы получить.")
        return
    bot.reply_to(m, f"✨ {name}, твой текущий размер груди: <b>{row[0][0]}</b> {boob_word(row[0][0])} 🍒")

@bot.message_handler(commands=['top'])
def cmd_top(m):
    chat_id = str(m.chat.id)
    rows = db_execute("SELECT user_id,size FROM boobs WHERE chat_id=? ORDER BY size DESC LIMIT 10",(chat_id,),fetch=True)
    if not rows:
        bot.reply_to(m,"Нет данных 😅")
        return
    text = "🏆 <b>ТОП груди</b>:\n\n"
    for i,(uid,size) in enumerate(rows,start=1):
        name = get_display_name(chat_id,uid) or f"<a href='tg://user?id={uid}'>Пользователь</a>"
        text += f"{i}. {name} — <b>{size}</b> {boob_word(size)} 🍒\n"
    bot.reply_to(m,text)

@bot.message_handler(commands=['имя'])
def set_name(m):
    chat_id = str(m.chat.id)
    user_id = str(m.from_user.id)
    parts = m.text.split(maxsplit=1)
    if len(parts)<2:
        bot.reply_to(m,"Используй: /имя Лох")
        return
    name_text = parts[1]
    db_execute("INSERT OR REPLACE INTO names(chat_id,user_id,display_name) VALUES (?,?,?)",
               (chat_id,user_id,name_text))
    bot.reply_to(m,f"🎉 Ваше имя изменено на '{name_text}'")

@bot.message_handler(commands=['dr'])
def birthdays(m):
    chat_id = str(m.chat.id)
    user_id = str(m.from_user.id)
    cmd = m.text.split()
    
    if len(cmd) == 1:
        row = db_execute("SELECT date FROM birthdays WHERE chat_id=? AND user_id=?", (chat_id, user_id), fetch=True)
        if row:
            bot.reply_to(m,f"🎂 Твой день рождения: {row[0][0]}")
        else:
            bot.reply_to(m,"🎂 Ты ещё не указал день рождения")
        return

    if cmd[1].lower() == "all":
        rows = db_execute("SELECT user_id,date FROM birthdays WHERE chat_id=?", (chat_id,), fetch=True)
        if not rows:
            bot.reply_to(m,"🎂 Нет дней рождения 😅")
            return
        text = "🎂 Дни рождения чата:\n"
        for uid,date in rows:
            name = get_display_name(chat_id,uid) or f"<a href='tg://user?id={uid}'>Пользователь</a>"
            text += f"{name} — {date}\n"
        bot.reply_to(m,text)
        return

    date_text = cmd[1]
    if not re.match(r"\d{2}\.\d{2}\.\d{4}", date_text):
        bot.reply_to(m,"Используй формат: /dr дд.мм.гггг")
        return

    db_execute("INSERT OR REPLACE INTO birthdays(chat_id,user_id,date) VALUES (?,?,?)",
               (chat_id,user_id,date_text))
    bot.reply_to(m,f"🎂 День рождения сохранён: {date_text}")

# ==========================
# ОБЩИЕ СООБЩЕНИЯ
# ==========================
@bot.message_handler(func=lambda m: True)
def general_handler(m):
    text = m.text.lower()
    chat_id = m.chat.id
    user_id = m.from_user.id
    name = get_display_name(chat_id, user_id) or m.from_user.first_name

    if "сиськи" in text:
        delta, new_size = change_boobs(chat_id, user_id)
        if delta == 0:
            bot.reply_to(m, f"Ой, а ты уже пробовал сегодня 😅\nТвой размер груди равен <b>{new_size}</b> {boob_word(new_size)} 🍒")
        else:
            bot.reply_to(m, f"🍒 {name}, твой размер груди вырос на <b>{delta}</b>, теперь твой размер груди равен <b>{new_size}</b> {boob_word(new_size)} 🍒")
        return

    if "кто же я" in text:
        answer = whoami(chat_id, user_id)
        bot.reply_to(m, answer)
        return

# ==========================
# ПОКУПКА
# ==========================
PROVIDER_TOKEN = ""  # вставь сюда provider_token Telegram Stars

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
        provider_token=PROVIDER_TOKEN,
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
                   (chat_id, uid, size, datetime.date.today().isoformat()))
        bot.send_message(int(chat_id), f"🎉 Пользователь купил +1 груди!\n"
                                       f"Новый размер: <b>{size}</b> {boob_word(size)} 🍒")

# ==========================
# ПУСК
# ==========================
if __name__ == "__main__":
    bot.infinity_polling(skip_pending=True)
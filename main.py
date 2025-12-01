# main.py
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

ADMIN_USERNAME = "Sugar_Daddy_rip"
PHOTO_DIR = "photos"
DONATE_PRICE = 10

def get_stored_name(chat_id, user_id):
    row = db_execute("SELECT display_name FROM names WHERE chat_id=? AND user_id=?", (str(chat_id), str(user_id)), fetch=True)
    if row:
        return row[0]["display_name"]
    return None

def get_user_name_fallback(chat_id, user_id):
    try:
        member = bot.get_chat_member(chat_id, user_id)
        user = member.user
        if getattr(user, "last_name", None):
            return f"{user.first_name} {user.last_name}"
        return user.first_name or "Пользователь"
    except Exception:
        return "Пользователь"

def get_display_name(chat_id, user_id):
    name = get_stored_name(chat_id, user_id)
    if name:
        return name
    return get_user_name_fallback(chat_id, user_id)

def change_size(table, chat_id, user_id, delta_range=(-10,10)):
    today = datetime.date.today().isoformat()
    chat, user = str(chat_id), str(user_id)
    row = db_execute(f"SELECT * FROM {table} WHERE chat_id=? AND user_id=?", (chat, user), fetch=True)
    if row:
        last = row[0]["last_date"]
        size_key = "size" if table=="boobs" else ("size_mm" if table=="klitor" else "size_cm")
        size = row[0][size_key]
    else:
        last = None
        size = 0
    if last == today:
        return 0, size
    delta = random.randint(delta_range[0], delta_range[1])
    if size + delta < 0:
        delta = -size
    new_size = size + delta
    size_key = "size" if table=="boobs" else ("size_mm" if table=="klitor" else "size_cm")
    db_execute(f"INSERT OR REPLACE INTO {table}(chat_id,user_id,{size_key},last_date) VALUES (?,?,?,?)",
               (chat, user, new_size, today))
    return delta, new_size

def whoami(chat_id, user_id):
    today = datetime.date.today().isoformat()
    chat, user = str(chat_id), str(user_id)
    row = db_execute("SELECT choice,date FROM whoami WHERE chat_id=? AND user_id=?", (chat, user), fetch=True)
    if row and row[0]["date"] == today:
        return row[0]["choice"]
    choice = random.choice(["ты лох 😏", "удивительно, но сегодня ты не лох 🎉"])
    db_execute("INSERT OR REPLACE INTO whoami(chat_id,user_id,choice,date) VALUES (?,?,?,?)",
               (chat, user, choice, today))
    return choice

# === Основные команды ===
@bot.message_handler(commands=['komands'])
def cmd_commands(m):
    bot.reply_to(m,
                 "Привет! Я бот с ростом органов 😏\n\n"
                 "Команды:\n"
                 "/sisi — получить рост груди на сегодня 🍒\n"
                 "/klitor — отрастить клитор (мм) 🍆\n"
                 "/hui — отрастить хуй (см) 🍌\n"
                 "/my — показать свои размеры 🍒🍆🍌\n"
                 "/buy — донат 10 ⭐ и получить буст или фото 🎁\n"
                 "/topsisi — топ по сиськам 😎\n"
                 "/topklitor — топ по клитору 😎\n"
                 "/tophui — топ по хуям 😎\n"
                 "/name <имя> — установить своё имя 😏\n"
                 "/dr <дд.мм.гггг> — записать день рождения 🎂\n"
                 "/dr all — список ДР в чате 🎂\n"
                 "/kto — узнать, кто ты сегодня 😉")

# === Игровые команды ===
@bot.message_handler(commands=['sisi'])
def cmd_sisi(m):
    chat_id, user_id = m.chat.id, m.from_user.id
    name = get_display_name(chat_id, user_id)
    delta, new_size = change_size("boobs", chat_id, user_id)
    if delta == 0:
        bot.reply_to(m, f"Ой, а ты уже пробовал сегодня 😅\nТвой текущий размер груди — <b>{new_size}</b> 🍒")
    else:
        sign = f"{delta:+d}"
        bot.reply_to(m, f"🍒 {name}, твой размер груди вырос на <b>{sign}</b>, теперь твой размер груди — <b>{new_size}</b> 🍒")

@bot.message_handler(commands=['klitor'])
def cmd_klitor(m):
    chat_id, user_id = m.chat.id, m.from_user.id
    name = get_display_name(chat_id, user_id)
    delta, new_size = change_size("klitor", chat_id, user_id, (-10,10))
    if delta == 0:
        bot.reply_to(m, f"Ой, а ты уже пробовал сегодня 😅\nТекущий клитор — <b>{new_size} мм</b> 🍆")
    else:
        sign = f"{delta:+d}"
        bot.reply_to(m, f"🍆 {name}, твой клитор вырос на <b>{sign} мм</b>, теперь — <b>{new_size} мм</b> 🍆")

@bot.message_handler(commands=['hui'])
def cmd_hui(m):
    chat_id, user_id = m.chat.id, m.from_user.id
    name = get_display_name(chat_id, user_id)
    delta, new_size = change_size("hui", chat_id, user_id, (-10,10))
    if delta == 0:
        bot.reply_to(m, f"Ой, а ты уже пробовал сегодня 😅\nТекущий хуй — <b>{new_size} см</b> 🍌")
    else:
        sign = f"{delta:+d}"
        bot.reply_to(m, f"🍌 {name}, твой хуй вырос на <b>{sign} см</b>, теперь — <b>{new_size} см</b> 🍌")

@bot.message_handler(commands=['my'])
def cmd_my(m):
    chat_id, user_id = str(m.chat.id), str(m.from_user.id)
    boobs = db_execute("SELECT size FROM boobs WHERE chat_id=? AND user_id=?", (chat_id,user_id), fetch=True)
    klitor = db_execute("SELECT size_mm FROM klitor WHERE chat_id=? AND user_id=?", (chat_id,user_id), fetch=True)
    hui = db_execute("SELECT size_cm FROM hui WHERE chat_id=? AND user_id=?", (chat_id,user_id), fetch=True)
    bot.reply_to(m,
                 f"✨ {get_display_name(m.chat.id, m.from_user.id)}, ваши размеры:\n"
                 f"Грудь: <b>{boobs[0]['size'] if boobs else 0}</b> 🍒\n"
                 f"Клитор: <b>{klitor[0]['size_mm'] if klitor else 0} мм</b> 🍆\n"
                 f"Хуй: <b>{hui[0]['size_cm'] if hui else 0} см</b> 🍌")

# === Топы ===
def top_text(table, chat_id, unit):
    rows = db_execute(f"SELECT user_id,{ 'size' if table=='boobs' else ('size_mm' if table=='klitor' else 'size_cm') } AS s FROM {table} WHERE chat_id=? ORDER BY s DESC LIMIT 10", (str(chat_id),), fetch=True)
    if not rows: return "Пусто 😅"
    text = f"🏆 ТОП {table}:\n\n"
    for i,r in enumerate(rows,start=1):
        name = get_display_name(chat_id,r['user_id'])
        text += f"{i}. {name} — {r['s']} {unit}\n"
    return text

@bot.message_handler(commands=['topsisi'])
def cmd_topsisi(m):
    bot.reply_to(m, top_text("boobs", m.chat.id, "🍒"))

@bot.message_handler(commands=['topklitor'])
def cmd_topklitor(m):
    bot.reply_to(m, top_text("klitor", m.chat.id, "мм 🍆"))

@bot.message_handler(commands=['tophui'])
def cmd_tophui(m):
    bot.reply_to(m, top_text("hui", m.chat.id, "см 🍌"))

# === Донат команда /buy ===
@bot.message_handler(commands=['buy'])
def cmd_buy(m):
    chat_id, user_id = m.chat.id, m.from_user.id
    choice = random.choice(['photo','boost'])
    if choice=='photo':
        photos = [os.path.join(PHOTO_DIR,f) for f in os.listdir(PHOTO_DIR) if f.lower().endswith(('.jpg','.png','.jpeg'))]
        if not photos:
            bot.reply_to(m,"Нет фото для отправки 😅")
            return
        photo_path = random.choice(photos)
        with open(photo_path,'rb') as p:
            bot.send_photo(chat_id,p)
        bot.reply_to(m,"🎉 Вы получили рандомное фото!")
    else:
        game_choice = random.choice(['boobs','klitor','hui'])
        if game_choice=='boobs':
            delta = random.randint(-10,10)
            db_execute("UPDATE boobs SET size=size+? WHERE chat_id=? AND user_id=?", (delta,str(chat_id),str(user_id)))
            new_size = db_execute("SELECT size FROM boobs WHERE chat_id=? AND user_id=?", (str(chat_id),str(user_id)), fetch=True)[0]['size']
            bot.reply_to(m,f"🎉 Ваш размер груди изменился на <b>{delta:+d}</b>, теперь — <b>{new_size}</b> 🍒")
        elif game_choice=='klitor':
            delta = random.randint(-10,10)
            db_execute("UPDATE klitor SET size_mm=size_mm+? WHERE chat_id=? AND user_id=?", (delta,str(chat_id),str(user_id)))
            new_size = db_execute("SELECT size_mm FROM klitor WHERE chat_id=? AND user_id=?", (str(chat_id),str(user_id)), fetch=True)[0]['size_mm']
            bot.reply_to(m,f"🎉 Ваш клитор изменился на <b>{delta:+d} мм</b>, теперь — <b>{new_size}</b> 🍆")
        elif game_choice=='hui':
            delta = random.randint(-10,10)
            db_execute("UPDATE hui SET size_cm=size_cm+? WHERE chat_id=? AND user_id=?", (delta,str(chat_id),str(user_id)))
            new_size = db_execute("SELECT size_cm FROM hui WHERE chat_id=? AND user_id=?", (str(chat_id),str(user_id)), fetch=True)[0]['size_cm']
            bot.reply_to(m,f"🎉 Ваш хуй изменился на <b>{delta:+d} см</b>, теперь — <b>{new_size}</b> 🍌")

# === Имя / ДР / Кто ===
@bot.message_handler(commands=['name'])
def cmd_name(m):
    parts = m.text.split(maxsplit=1)
    if len(parts)<2:
        bot.reply_to(m,"Используй: /name ТвоёИмя")
        return
    db_execute("INSERT OR REPLACE INTO names(chat_id,user_id,display_name) VALUES (?,?,?)",
               (str(m.chat.id), str(m.from_user.id), parts[1].strip()))
    bot.reply_to(m,f"🎉 Ваше имя изменено на '{parts[1].strip()}'")

@bot.message_handler(commands=['dr'])
def cmd_dr(m):
    parts = m.text.split()
    chat_id, user_id = str(m.chat.id), str(m.from_user.id)
    if len(parts)==1:
        row = db_execute("SELECT date FROM birthdays WHERE chat_id=? AND user_id=?", (chat_id,user_id), fetch=True)
        if row:
            bot.reply_to(m,f"🎂 Твой день рождения: {row[0]['date']}")
        else:
            bot.reply_to(m,"🎂 Ты ещё не указал день рождения")
        return
    if parts[1].lower()=="all":
        rows = db_execute("SELECT user_id,date FROM birthdays WHERE chat_id=?", (chat_id,), fetch=True)
        if not rows:
            bot.reply_to(m,"🎂 Нет дней рождения 😅")
            return
        text = "🎂 Дни рождения чата:\n"
        for r in rows:
            name = get_display_name(chat_id,r['user_id'])
            text += f"{name} — {r['date']}\n"
        bot.reply_to(m,text)
        return
    date_text = parts[1]
    if not re.match(r"\d{2}\.\d{2}\.\d{4}$", date_text):
        bot.reply_to(m,"Используй формат: /dr дд.мм.гггг")
        return
    db_execute("INSERT OR REPLACE INTO birthdays(chat_id,user_id,date) VALUES (?,?,?)",(chat_id,user_id,date_text))
    bot.reply_to(m,f"🎂 День рождения сохранён: {date_text}")

@bot.message_handler(commands=['kto'])
def cmd_kto(m):
    res = whoami(str(m.chat.id), str(m.from_user.id))
    bot.reply_to(m,res)

# === Запуск бота ===
if __name__=="__main__":
    bot.infinity_polling(skip_pending=True)
import sqlite3
import telebot
from telebot.types import LabeledPrice

import random
import datetime
import re

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import io

import os
TOKEN = os.environ.get("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")


# ==========================
#        БАЗА ДАННЫХ
# ==========================

def db_execute(query, params=(), fetch=False):
    conn = sqlite3.connect("boobs.db")
    cur = conn.cursor()
    cur.execute(query, params)
    data = cur.fetchall() if fetch else None
    conn.commit()
    conn.close()
    return data

db_execute("""
CREATE TABLE IF NOT EXISTS boobs (
    chat_id TEXT,
    user_id TEXT,
    size INTEGER,
    last_date TEXT,
    PRIMARY KEY(chat_id, user_id)
)
""")

db_execute("""
CREATE TABLE IF NOT EXISTS settings (
    chat_id TEXT PRIMARY KEY,
    r25 INTEGER,
    r18 INTEGER,
    r16 INTEGER,
    r14 INTEGER,
    r12 INTEGER,
    r0 INTEGER
)
""")


# ==========================
#    ПОМОЩНИКИ
# ==========================

def has_permission(user_id):
    return str(user_id) in ["5356165089", "6219863577", "8030707743"]

def random_boobs(chat_id):
    settings = db_execute("SELECT r25,r18,r16,r14,r12,r0 FROM settings WHERE chat_id=?", (chat_id,), fetch=True)
    if not settings:
        weights = [1, 5, 10, 15, 20, 30]
    else:
        weights = settings[0]

    size_options = [25, 18, 16, 14, 12, 0]
    return random.choices(size_options, weights)[0]


# ==========================
#     СТАРТОВЫЕ КОМАНДЫ
# ==========================

@bot.message_handler(commands=['start'])
def cmd_start(m):
    bot.reply_to(m, "Привет! Я бот с грудями 😏\n\nКоманды:\n"
                    "/give — выдать случайный размер\n"
                    "/my — показать мой размер\n"
                    "/buy_boobs — купить +1 ⭐\n"
                    "/top — топ участников\n"
                    "/stats — статистика чата\n"
                    "/add — добавить размер\n")


# ==========================
#     ГЛАВНАЯ ЛОГИКА
# ==========================

@bot.message_handler(commands=['give'])
def cmd_give(m):
    chat_id = str(m.chat.id)
    user_id = str(m.from_user.id)

    today = datetime.date.today().isoformat()

    row = db_execute("SELECT size,last_date FROM boobs WHERE chat_id=? AND user_id=?", (chat_id, user_id), fetch=True)

    if row and row[0][1] == today:
        bot.reply_to(m, "Ты уже получал сегодня 😏")
        return

    new_size = random_boobs(chat_id)

    if not row:
        db_execute("INSERT INTO boobs VALUES (?,?,?,?)", (chat_id, user_id, new_size, today))
    else:
        db_execute("UPDATE boobs SET size=?, last_date=? WHERE chat_id=? AND user_id=?",
                   (new_size, today, chat_id, user_id))

    bot.reply_to(m, f"Сегодня твой размер: <b>{new_size}</b> 🍒")


@bot.message_handler(commands=['my'])
def cmd_my(m):
    chat_id = str(m.chat.id)
    user_id = str(m.from_user.id)

    row = db_execute("SELECT size FROM boobs WHERE chat_id=? AND user_id=?", (chat_id, user_id), fetch=True)

    if not row:
        bot.reply_to(m, "У тебя ещё нет размера 😅 Введи /give")
        return

    bot.reply_to(m, f"✨ Твой размер груди: <b>{row[0][0]}</b>")


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

    msg = bot.send_message(m.chat.id, "Отлично, один момент…")

    # пробуем найти участника
    try:
        members = bot.get_chat_administrators(m.chat.id)
    except:
        bot.edit_message_text("Ошибка.", m.chat.id, msg.message_id)
        return

    user_id = None
    for adm in members:
        if adm.user.username and adm.user.username.lower() == target[1:].lower():
            user_id = adm.user.id
            break

    if not user_id:
        bot.edit_message_text("Не нашёл пользователя 😢", m.chat.id, msg.message_id)
        return

    chat_id = str(m.chat.id)
    uid = str(user_id)

    row = db_execute("SELECT size FROM boobs WHERE chat_id=? AND user_id=?", (chat_id, uid), fetch=True)
    size = row[0][0] if row else 0
    size += add

    db_execute("INSERT OR REPLACE INTO boobs(chat_id,user_id,size,last_date) VALUES (?,?,?,?)",
               (chat_id, uid, size, ""))

    bot.edit_message_text(f"Готово! @{target[1:]} теперь имеет размер {size} 🍒", m.chat.id, msg.message_id)


# ==========================
#     ТОП + СТАТИСТИКА
# ==========================

@bot.message_handler(commands=['top'])
def cmd_top(m):
    chat_id = str(m.chat.id)

    rows = db_execute("SELECT user_id,size FROM boobs WHERE chat_id=? ORDER BY size DESC LIMIT 10", (chat_id,), fetch=True)

    if not rows:
        bot.reply_to(m, "Пусто 😅")
        return

    text = "🏆 <b>ТОП груди</b>:\n\n"
    for i, (uid, size) in enumerate(rows, start=1):
        text += f"{i}. <a href='tg://user?id={uid}'>Пользователь</a> — <b>{size}</b>\n"

    bot.reply_to(m, text)


@bot.message_handler(commands=['stats'])
def cmd_stats(m):
    chat_id = str(m.chat.id)

    rows = db_execute("SELECT size FROM boobs WHERE chat_id=?", (chat_id,), fetch=True)
    if not rows:
        bot.reply_to(m, "Нет данных 😅")
        return

    sizes = [r[0] for r in rows]

    fig, ax = plt.subplots()
    ax.hist(sizes)
    ax.set_title("Распределение размеров груди")
    ax.set_xlabel("Размер")
    ax.set_ylabel("Количество")

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    bot.send_photo(m.chat.id, buf)
    buf.close()


# ==========================
#     ОПЛАТА ⭐ STAR
# ==========================

@bot.message_handler(commands=['buy_boobs'])
def cmd_buy(m):
    chat_id = str(m.chat.id)
    uid = str(m.from_user.id)

    star_price = 5 * 1000  # 5 звёзд

    payload = f"buy_boobs_{chat_id}_{uid}"

    prices = [LabeledPrice(label="1 единица груди", amount=star_price)]

    bot.send_invoice(
        chat_id=m.chat.id,
        title="Покупка груди",
        description="Покупка +1 груди за 5 ⭐",
        invoice_payload=payload,
        currency="XTR",
        prices=prices,
        provider_token="",  # ДЛЯ ЗВЁЗД НЕ НУЖНО
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
#     ПУСК
# ==========================

if __name__ == "__main__":
    bot.infinity_polling(skip_pending=True)
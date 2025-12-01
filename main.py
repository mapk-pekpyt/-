import logging
from datetime import datetime, date
import random
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes
)

logging.basicConfig(level=logging.INFO)

TOKEN = "YOUR_TOKEN_HERE"
ADMIN_USERNAME = "Sugar_Daddy_rip"

# ХРАНИЛИЩЕ ДАННЫХ
boobs = {}          # user_id → int
last_sisi = {}      # user_id → date
names = {}          # user_id → str
kto_cache = {}      # user_id → (str, date)
birthdays = {}      # chat_id → {user_id: date}


# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ --- #

def format_boobs(n: int) -> str:
    if n % 10 == 1 and n % 100 != 11:
        return f"{n} размер груди"
    elif n % 10 in (2, 3, 4) and n % 100 not in (12, 13, 14):
        return f"{n} размера груди"
    else:
        return f"{n} размеров груди"


def get_name(user):
    return names.get(user.id, user.first_name)


async def admin_only(update: Update):
    await update.message.reply_text("❌ Эта команда только для администратора.")


# --- КОМАНДЫ --- #

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! 😏 Я бот с грудями и хаосом 🍒\n"
        "Проверяю размеры, запоминаю дни рождения и иногда определяю, кто ты сегодня 😎\n"
        "Напиши /commands чтобы увидеть мои умения! 🚀"
    )


async def commands(update: Update, context):
    await update.message.reply_text(
        "📋 Список команд:\n"
        "/sisi — вырастить грудь (1 раз в день)\n"
        "/my — показать мой размер\n"
        "/top — топ по размерам\n"
        "/stats — статистика чата\n"
        "/birthday ДД.ММ.ГГГГ — сохранить ДР\n"
        "/birthdays — все ДР чата\n"
        "/kto — узнать кто ты сегодня\n"
        "/name Имя — установить себе имя\n\n"
        "👑 Админ команды:\n"
        "/admin_add @user X — выдать X размера\n"
        "/admin_name @user Имя — изменить имя"
    )


async def sisi(update: Update, context):
    user = update.message.from_user
    uid = user.id
    today = date.today()

    if uid in last_sisi and last_sisi[uid] == today:
        size = boobs.get(uid, 0)
        await update.message.reply_text(
            f"😒 Ты уже пробовал сегодня!\n"
            f"Твой текущий размер: {format_boobs(size)}"
        )
        return

    grow = random.randint(-10, 10)
    old = boobs.get(uid, 0)

    # Если выпадет отрицательное — не допускаем уход в минус
    if old + grow < 0:
        grow = -old

    new = old + grow
    boobs[uid] = new
    last_sisi[uid] = today

    await update.message.reply_text(
        f"✨ Твой размер груди вырос на {grow:+}!\n"
        f"Теперь у тебя {format_boobs(new)} 💖"
    )


async def my(update: Update, context):
    uid = update.message.from_user.id
    size = boobs.get(uid, 0)
    await update.message.reply_text(f"У тебя сейчас {format_boobs(size)} 😏")


async def top(update: Update, context):
    if not boobs:
        await update.message.reply_text("Топ пуст 🥲")
        return

    sorted_users = sorted(boobs.items(), key=lambda x: x[1], reverse=True)
    text = "🏆 Топ участников по размеру груди:\n\n"

    for uid, size in sorted_users[:10]:
        text += f"{format_boobs(size)} — {uid}\n"

    await update.message.reply_text(text)


async def stats(update: Update, context):
    chat_id = update.message.chat_id
    if chat_id not in birthdays:
        count = 0
    else:
        count = len(birthdays[chat_id])

    await update.message.reply_text(
        f"📊 В чате сохранено дней рождения: {count}"
    )


async def birthday(update: Update, context):
    chat_id = update.message.chat_id
    user = update.message.from_user

    if len(context.args) != 1:
        await update.message.reply_text("Формат: /birthday ДД.ММ.ГГГГ")
        return

    try:
        bday = datetime.strptime(context.args[0], "%d.%m.%Y").date()
    except:
        await update.message.reply_text("Неверный формат даты!")
        return

    birthdays.setdefault(chat_id, {})
    birthdays[chat_id][user.id] = bday

    await update.message.reply_text("🎉 День рождения сохранён!")


async def birthdays_cmd(update: Update, context):
    chat_id = update.message.chat_id
    if chat_id not in birthdays or not birthdays[chat_id]:
        await update.message.reply_text("В этом чате нет сохранённых дней рождения.")
        return

    text = "🎂 Дни рождения чата:\n\n"
    for uid, bday in birthdays[chat_id].items():
        text += f"{uid}: {bday.strftime('%d.%m.%Y')}\n"

    await update.message.reply_text(text)


async def kto(update: Update, context):
    user = update.message.from_user
    uid = user.id
    today = date.today()

    if uid in kto_cache and kto_cache[uid][1] == today:
        res = kto_cache[uid][0]
    else:
        res = random.choice([
            "ты лох 🤡", 
            "удивительно, но сегодня ты не лох 😎"
        ])
        kto_cache[uid] = (res, today)

    await update.message.reply_text(f"🌀 Сегодня {res}")


async def name(update: Update, context):
    user = update.message.from_user
    if not context.args:
        await update.message.reply_text("Формат: /name НовоеИмя")
        return

    new_name = " ".join(context.args)
    names[user.id] = new_name

    await update.message.reply_text(f"Теперь твоё имя: {new_name} 😎")


# --- АДМИН КОМАНДЫ --- #

async def admin_add(update: Update, context):
    user = update.message.from_user
    if user.username != ADMIN_USERNAME:
        return await admin_only(update)

    if len(context.args) < 2:
        return await update.message.reply_text("Формат: /admin_add @user X")

    username = context.args[0].replace("@", "")
    amount = int(context.args[1])

    # Поиск юзера по имени в кэше (мы храним только айди)
    target_id = None
    for uid in boobs.keys() | names.keys():
        if context.bot.get_chat(uid).username == username:
            target_id = uid
            break

    if not target_id:
        return await update.message.reply_text("Юзер не найден!")

    boobs[target_id] = boobs.get(target_id, 0) + amount

    await update.message.reply_text(
        f"Админ выдал {format_boobs(amount)} пользователю @{username} 👑"
    )


async def admin_name(update: Update, context):
    user = update.message.from_user
    if user.username != ADMIN_USERNAME:
        return await admin_only(update)

    if len(context.args) < 2:
        return await update.message.reply_text("Формат: /admin_name @user Имя")

    username = context.args[0].replace("@", "")
    new_name = " ".join(context.args[1:])

    target_id = None
    for uid in boobs.keys() | names.keys():
        if context.bot.get_chat(uid).username == username:
            target_id = uid
            break

    if not target_id:
        return await update.message.reply_text("Юзер не найден!")

    names[target_id] = new_name
    await update.message.reply_text(f"Имя пользователя @{username} изменено на: {new_name}")


# --- ЗАПУСК --- #

async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("commands", commands))
    app.add_handler(CommandHandler("sisi", sisi))
    app.add_handler(CommandHandler("my", my))
    app.add_handler(CommandHandler("top", top))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("birthday", birthday))
    app.add_handler(CommandHandler("birthdays", birthdays_cmd))
    app.add_handler(CommandHandler("kto", kto))
    app.add_handler(CommandHandler("name", name))

    app.add_handler(CommandHandler("admin_add", admin_add))
    app.add_handler(CommandHandler("admin_name", admin_name))

    print("BOT RUNNING...")
    await app.run_polling()

import asyncio
asyncio.run(main())
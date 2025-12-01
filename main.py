import asyncio
import random
from datetime import datetime
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message

TOKEN = "ТВОЙ_ТОКЕН_БОТА"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Хранилища данных
user_boobs = {}          # user_id: int (общий размер груди)
last_sisi_date = {}      # user_id: "YYYY-MM-DD"
user_names = {}          # user_id: custom name
daily_kto = {}           # user_id: {"date": str, "value": str}

# ===== УТИЛИТЫ =====

def get_name(message: Message):
    """Имя пользователя: сначала кастомное, если нет — username, если нет — first_name."""
    user_id = message.from_user.id
    if user_id in user_names:
        return user_names[user_id]
    if message.from_user.username:
        return message.from_user.username
    return message.from_user.first_name or "Неизвестный"

# ===== КОМАНДА /sisi =====
@dp.message(F.text.lower() == "/sisi")
async def cmd_sisi(message: Message):
    user_id = message.from_user.id
    name = get_name(message)
    today = datetime.now().strftime("%Y-%m-%d")

    current_size = user_boobs.get(user_id, 0)

    # Если сегодня уже использовал
    if last_sisi_date.get(user_id) == today:
        await message.reply(
            f"Ой, а ты уже пробовал сегодня 😅\n"
            f"Твой текущий размер груди — {current_size} 🍒"
        )
        return

    # Выдаём новый прирост
    growth = random.randint(1, 10)
    new_size = current_size + growth
    user_boobs[user_id] = new_size
    last_sisi_date[user_id] = today

    await message.reply(
        f"🍒 {name}, твой размер груди вырос на +{growth},\n"
        f"теперь твой размер груди — {new_size} 🍒"
    )

# ===== КОМАНДА /my =====
@dp.message(F.text.lower() == "/my")
async def cmd_my(message: Message):
    user_id = message.from_user.id
    size = user_boobs.get(user_id, 0)
    name = get_name(message)
    await message.reply(f"{name}, твой текущий размер груди — {size} 🍒")

# ===== КОМАНДА /kto =====
@dp.message(F.text.lower() == "/kto")
async def cmd_kto(message: Message):
    user_id = message.from_user.id
    today = datetime.now().strftime("%Y-%m-%d")

    if user_id in daily_kto and daily_kto[user_id]["date"] == today:
        await message.reply(f"Сегодня ты — {daily_kto[user_id]['value']} 😏")
        return

    variants = [
        "секси пельмешек 😈",
        "наглый развратник 😏",
        "милая булочка 😊",
        "сладенький пирожочек 😘",
        "главная сиська дня 😎",
        "нежный цветочек 🌸"
    ]

    choice = random.choice(variants)
    daily_kto[user_id] = {"date": today, "value": choice}

    await message.reply(f"Сегодня ты — {choice} 😏")

# ===== КОМАНДА /name =====
@dp.message(F.text.lower().startswith("/name "))
async def cmd_name(message: Message):
    user_id = message.from_user.id
    new_name = message.text[6:].strip()

    if not new_name:
        await message.reply("Напиши имя после команды, пример:\n/name Красавчик")
        return

    user_names[user_id] = new_name
    await message.reply(f"Теперь твоё имя — {new_name} 😎")

# ===== АДМИН КОМАНДА /add =====
ADMIN_USERNAME = "Sugar_Daddy_rip"

@dp.message(F.text.lower().startswith("/add "))
async def cmd_add(message: Message):
    if (message.from_user.username or "").lower() != ADMIN_USERNAME.lower():
        return  # игнор, если не админ

    parts = message.text.split()
    if len(parts) != 3:
        await message.reply("Использование: /add @username 10")
        return

    _, user_tag, value = parts
    try:
        value = int(value)
    except:
        await message.reply("Размер должен быть числом.")
        return

    if not user_tag.startswith("@"):
        await message.reply("Укажи username через @")
        return

    # В группах Telegram не предоставляет user_id по @username
    # Поэтому админ должен применять /add ТОЛЬКО как ответ на сообщение
    if not message.reply_to_message:
        await message.reply("Ответь этой командой на сообщение нужного пользователя.")
        return

    target_id = message.reply_to_message.from_user.id
    user_boobs[target_id] = user_boobs.get(target_id, 0) + value

    await message.reply(f"Добавил +{value} к размеру груди пользователя.")

# ===== КОМАНДА /komands =====
@dp.message(F.text.lower() == "/komands")
async def cmd_commands(message: Message):
    await message.reply(
        "📌 Список команд:\n"
        "/sisi — получить прирост груди (1 раз в день)\n"
        "/my — узнать свой размер\n"
        "/kto — кто ты сегодня\n"
        "/name — изменить своё имя\n"
        "/top — топ сисек чата\n"
        "/komands — список команд"
    )

# ===== КОМАНДА /top =====
@dp.message(F.text.lower() == "/top")
async def cmd_top(message: Message):
    if not user_boobs:
        await message.reply("Топ пуст 😔")
        return

    sorted_users = sorted(user_boobs.items(), key=lambda x: x[1], reverse=True)
    lines = ["🏆 ТОП сисек:\n"]

    for i, (user_id, size) in enumerate(sorted_users, start=1):
        name = user_names.get(user_id, f"User {user_id}")
        lines.append(f"{i}. {name} — {size} 🍒")

    await message.reply("\n".join(lines))

# ===== СТАРТ =====
async def main():
    print("Bot started!")
    await dp.start_polling(bot)

asyncio.run(main())
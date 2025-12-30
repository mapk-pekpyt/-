import os
import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types

# --- Загружаем токены из переменных окружения ---
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Telegram Bot token
TRIBUTE_API_KEY = os.getenv("TRIBUTE_API_KEY")  # Tribute API key
TRIBUTE_PAYMENT_URL = "https://t.me/tribute/app?startapp=poWz"  # тариф Неделя

if not BOT_TOKEN:
    raise Exception("BOT_TOKEN не задан! Установи переменную окружения.")
if not TRIBUTE_API_KEY:
    raise Exception("TRIBUTE_API_KEY не задан! Установи переменную окружения.")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- Команда /start ---
@dp.message(commands=["start"])
async def cmd_start(message: types.Message):
    await message.answer("Привет! Для теста оплаты используй /buy_week")

# --- Команда /buy_week ---
@dp.message(commands=["buy_week"])
async def buy_week(message: types.Message):
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("Оплатить Неделя — 100₽", url=TRIBUTE_PAYMENT_URL))
    await message.answer("Нажми кнопку и оплати в Tribute:", reply_markup=kb)
    await message.answer("После оплаты нажми /check_payment чтобы подтвердить.")

# --- Команда /check_payment ---
@dp.message(commands=["check_payment"])
async def check_payment(message: types.Message):
    async with aiohttp.ClientSession() as session:
        headers = {"Api-Key": TRIBUTE_API_KEY}
        async with session.get("https://tribute.tg/api/v1/payments", headers=headers) as resp:
            data = await resp.json()

    # Проверка: если есть хотя бы один платёж со статусом "paid"
    paid = any(payment.get("status") == "paid" for payment in data.get("payments", []))

    if paid:
        await message.answer("✅ Молодец! Оплата прошла!")
    else:
        await message.answer("❌ Платёж не найден. Попробуй позже.")

# --- Запуск бота ---
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
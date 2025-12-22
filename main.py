import asyncio
import logging
import sys
import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode

# ========== ПОЛУЧАЕМ ТОКЕН ИЗ ПЕРЕМЕННЫХ ОКРУЖЕНИЯ BOTHOST ==========
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Bothost передает токен здесь

if not BOT_TOKEN:
    print("❌ ОШИБКА: Токен не найден!")
    print("Вставьте токен бота в настройках Bothost:")
    print("1. Зайдите в проект на Bothost")
    print("2. Найдите поле 'BOT_TOKEN' или 'Токен бота'")
    print("3. Вставьте токен от @BotFather")
    print("4. Перезапустите бота")
    sys.exit(1)

# ========== ОСНОВНОЙ КОД ==========
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    try:
        # Создаем бота с реальным токеном
        bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
        dp = Dispatcher(storage=MemoryStorage())
        
        @dp.message(commands=['start'])
        async def cmd_start(message):
            await message.answer(
                "✅ **Бот запущен на Bothost!**\n\n"
                f"Ваш ID: `{message.from_user.id}`\n"
                f"Токен получен: ДА\n"
                f"Запуск через: main.py\n\n"
                "Теперь можно добавлять модули:",
                parse_mode="Markdown"
            )
        
        @dp.message()
        async def echo(message):
            await message.answer("Напишите /start для проверки")
        
        logger.info(f"🚀 Бот запущен! Токен: {BOT_TOKEN[:10]}...")
        print("=" * 50)
        print("🤖 БОТ РАБОТАЕТ НА BOTHOST")
        print(f"🔐 Токен: {BOT_TOKEN[:15]}...")
        print("=" * 50)
        
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"❌ Ошибка запуска: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
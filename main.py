import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def main():
    try:
        # Создаем бота
        BOT_TOKEN = "ЗАМЕНИ_НА_СВОЙ_ТОКЕН"  # ⚠️ ЗАМЕНИ ЭТО!
        bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
        
        # Настраиваем диспетчер
        dp = Dispatcher(storage=MemoryStorage())
        
        # Регистрируем команды
        @dp.message()
        async def handle_all_messages(message):
            await message.answer("🤖 Бот работает!\n\nИспользуй /start")
        
        @dp.message(commands=['start'])
        async def cmd_start(message):
            await message.answer(
                "🚀 **Бот запущен!**\n\n"
                "Скоро здесь будет:\n"
                "• Управление ботами\n"
                "• Управление серверами\n"
                "• Mini App\n\n"
                "🔄 Обновляю код...",
                parse_mode="Markdown"
            )
        
        logger.info("🤖 Бот запускается...")
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("=" * 50)
    print("🤖 Bot Platform - Запуск")
    print("=" * 50)
    asyncio.run(main())
# main.py
import os
import importlib
import telebot
from config import TOKEN
from utils.db import init_db

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# Инициализация БД
init_db()

# Автозагрузка плагинов
print("Загрузка плагинов...")
for filename in os.listdir("plugins"):
    if filename.endswith(".py") and not filename.startswith("_"):
        module_name = filename[:-3]
        try:
            module = importlib.import_module(f"plugins.{module_name}")
            if hasattr(module, "register"):
                module.register(bot)
                print(f"Плагин загружен: {module_name}")
            else:
                print(f"Нет register() в {module_name}")
        except Exception as e:
            print(f"Ошибка загрузки {module_name}: {e}")

if __name__ == "__main__":
    print("Бот запущен и готов к работе!")
    bot.infinity_polling(skip_pending=True)
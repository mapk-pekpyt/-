import os
import importlib
import telebot
from config import TOKEN
from utils.db import init_db

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")
init_db()

print("Загружаю плагины...")
for file in os.listdir("plugins"):
    if file.endswith(".py") and not file.startswith("_"):
        name = file[:-3]
        try:
            module = importlib.import_module(f"plugins.{name}")
            if hasattr(module, "register"):
                module.register(bot)
                print(f"Загружен: {name}")
        except Exception as e:
            print(f"Ошибка {name}: {e}")

print("Бот запущен!")
bot.infinity_polling(skip_pending=True)
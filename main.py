# main.py
from telebot import TeleBot
from config import TOKEN
from plugins.loader import load_plugins
from utils.db import init_db, get_db_utils

bot = TeleBot(TOKEN, parse_mode="HTML")

# Инициализация БД (создает таблицы если нужно)
init_db()

# Передаём бот и утилиты при загрузке плагинов
load_plugins(bot, get_db_utils())

print("Bot started (plugins loaded).")
bot.infinity_polling(skip_pending=True)
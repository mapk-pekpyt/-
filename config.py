# config.py
import os

TOKEN = os.environ.get("BOT_TOKEN", "YOUR_TOKEN_HERE")
PROVIDER_TOKEN = os.environ.get("PROVIDER_TOKEN", "")  # если есть подключенный провайдер
DB_PATH = os.environ.get("DB_PATH", "boobs.db")
PHOTO_DIR = os.environ.get("PHOTO_DIR", "photos")
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "Sugar_Daddy_rip")
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise Exception("BOT_TOKEN محیطی تنظیم نشده!")

ADMIN_ID = int(os.environ.get("ADMIN_ID") or 1606291654)

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise Exception("DATABASE_URL محیطی تنظیم نشده!")

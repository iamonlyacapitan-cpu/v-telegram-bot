import os
import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler
from db import create_pool, init_db
from bot_handlers import start

BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise Exception("BOT_TOKEN محیطی تنظیم نشده!")

async def main():
    pool = await create_pool()
    await init_db(pool)

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.bot_data['db_pool'] = pool

    # دستور اصلی
    app.add_handler(CommandHandler("start", start))
    # ⚡ سایر handlers مثل show_plans, my_orders, wallet, admin_panel اضافه می‌شوند

    print("Bot is running...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())

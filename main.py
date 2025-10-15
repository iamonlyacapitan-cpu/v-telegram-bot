import asyncio
import os
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from db import init_db
from handlers import start, show_plans, my_orders, wallet, admin_panel

# داده‌های Render: BOT_TOKEN, ADMIN_ID, DATABASE_URL
BOT_TOKEN = os.environ.get("BOT_TOKEN")
DATABASE_URL = os.environ.get("DATABASE_URL")

async def main():
    # دیتابیس
    pool = await init_db(DATABASE_URL)
    print("Database initialized.")

    # ساخت ربات
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.bot_data['db_pool'] = pool

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(show_plans, pattern="^show_plans$"))
    app.add_handler(CallbackQueryHandler(my_orders, pattern="^my_orders$"))
    app.add_handler(CallbackQueryHandler(wallet, pattern="^wallet$"))
    app.add_handler(CallbackQueryHandler(admin_panel, pattern="^admin_panel$"))

    # اجرای ربات
    await app.start()
    await app.updater.start_polling()  # PTB 20+ هنوز باید Polling async باشه
    await app.updater.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())

import asyncio
import os
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from handlers import start, show_plans, my_orders, wallet, admin_panel
from db import init_db

BOT_TOKEN = os.environ["BOT_TOKEN"]

async def main():
    # اتصال به دیتابیس و ایجاد جداول اگر موجود نبود
    await init_db(os.environ["DATABASE_URL"])

    # ساخت اپلیکیشن
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # ثبت command و callback handler ها
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(show_plans, pattern="show_plans"))
    app.add_handler(CallbackQueryHandler(my_orders, pattern="my_orders"))
    app.add_handler(CallbackQueryHandler(wallet, pattern="wallet"))
    app.add_handler(CallbackQueryHandler(admin_panel, pattern="admin_panel"))

    print("Bot is running...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())

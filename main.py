import os
import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from handlers import start, show_plans, my_orders, wallet, admin_panel
from db import create_pool

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

async def main():
    # ساخت pool دیتابیس
    pool = await create_pool(DATABASE_URL)

    # ساخت app ربات
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # اضافه کردن pool به bot_data
    app.bot_data['db_pool'] = pool

    # ثبت command و callback handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(show_plans, pattern="^show_plans$"))
    app.add_handler(CallbackQueryHandler(my_orders, pattern="^my_orders$"))
    app.add_handler(CallbackQueryHandler(wallet, pattern="^wallet$"))
    app.add_handler(CallbackQueryHandler(admin_panel, pattern="^admin_panel$"))

    print("Bot is running...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())

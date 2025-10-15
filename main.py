import asyncio
from telegram.ext import ApplicationBuilder
from config import BOT_TOKEN
from bot_handlers import *

async def main():
    # ساخت اپلیکیشن Async
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # اضافه کردن هندلرها
    from telegram.ext import CommandHandler, CallbackQueryHandler

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(show_plans, pattern="show_plans"))
    app.add_handler(CallbackQueryHandler(my_orders, pattern="my_orders"))
    app.add_handler(CallbackQueryHandler(wallet, pattern="wallet"))
    app.add_handler(CallbackQueryHandler(admin_panel, pattern="admin_panel"))

    # اجرا
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())

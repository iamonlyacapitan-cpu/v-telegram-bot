import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from config import BOT_TOKEN
from db import create_pool, init_db
from bot_handlers import start, show_plans, my_orders, wallet, admin_panel

async def main():
    # اتصال به دیتابیس
    pool = await create_pool()
    await init_db(pool)

    # ساخت اپلیکیشن Async
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.bot_data['db_pool'] = pool

    # Command Handlers
    app.add_handler(CommandHandler("start", start))

    # Callback Handlers
    app.add_handler(CallbackQueryHandler(show_plans, pattern="show_plans"))
    app.add_handler(CallbackQueryHandler(my_orders, pattern="my_orders"))
    app.add_handler(CallbackQueryHandler(wallet, pattern="wallet"))
    app.add_handler(CallbackQueryHandler(admin_panel, pattern="admin_panel"))

    print("Bot is running...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())

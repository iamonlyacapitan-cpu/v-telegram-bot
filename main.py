import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from db import create_pool, init_db
from bot_handlers import start, wallet, show_plans, my_orders, admin_panel
from config import BOT_TOKEN

async def main():
    pool = await create_pool()
    await init_db(pool)

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.bot_data['db_pool'] = pool

    # Command Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("wallet", wallet))

    # Callback Handlers
    app.add_handler(CallbackQueryHandler(show_plans, pattern="show_plans"))
    app.add_handler(CallbackQueryHandler(my_orders, pattern="my_orders"))
    app.add_handler(CallbackQueryHandler(admin_panel, pattern="admin_panel"))

    print("Bot is running...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())

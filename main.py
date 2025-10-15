import os
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from handlers import start, show_plans, my_orders, wallet, admin_panel
from db import init_db, get_pool
import asyncio

BOT_TOKEN = os.environ["BOT_TOKEN"]

async def main():
    pool = await get_pool(os.environ["DATABASE_URL"])
    await init_db(pool)

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.bot_data['db_pool'] = pool

    # Command & Callback Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(show_plans, pattern="show_plans"))
    app.add_handler(CallbackQueryHandler(my_orders, pattern="my_orders"))
    app.add_handler(CallbackQueryHandler(wallet, pattern="wallet"))
    app.add_handler(CallbackQueryHandler(admin_panel, pattern="admin_panel"))

    # ✅ روش صحیح run_polling در نسخه 20+
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())

import asyncio
import os
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from handlers import start, show_plans, my_orders, wallet, admin_panel
from db import init_db, get_pool

BOT_TOKEN = os.environ["BOT_TOKEN"]

async def main():
    # ساخت Pool دیتابیس
    pool = await get_pool(os.environ["DATABASE_URL"])
    await init_db(pool)

    # ساخت اپلیکیشن
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # افزودن Pool دیتابیس به bot_data برای دسترسی handlerها
    app.bot_data['db_pool'] = pool

    # Command & Callback Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(show_plans, pattern="show_plans"))
    app.add_handler(CallbackQueryHandler(my_orders, pattern="my_orders"))
    app.add_handler(CallbackQueryHandler(wallet, pattern="wallet"))
    app.add_handler(CallbackQueryHandler(admin_panel, pattern="admin_panel"))

    # شروع ربات با run_polling
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())

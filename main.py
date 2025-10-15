import os
import asyncio
import logging
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from database import db
from handlers.user_handlers import user_handlers
from handlers.admin_handlers import admin_handlers

# تنظیمات logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# لود متغیرهای محیطی
load_dotenv()

async def main():
    """تابع اصلی اجرای ربات"""
    
    # اتصال به دیتابیس
    try:
        await db.connect()
        logger.info("✅ Connected to database successfully")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return
    
    # ایجاد اپلیکیشن
    bot_token = os.getenv('BOT_TOKEN')
    if not bot_token:
        logger.error("❌ BOT_TOKEN not found in environment variables")
        return
    
    application = Application.builder().token(bot_token).build()
    
    # ذخیره ADMIN_ID در context
    application.bot_data['ADMIN_ID'] = os.getenv('ADMIN_ID')
    
    # اضافه کردن هندلرهای کاربران
    for handler in user_handlers:
        application.add_handler(handler)
    
    # اضافه کردن هندلرهای ادمین
    for handler in admin_handlers:
        application.add_handler(handler)
    
    # هندلر شروع
    application.add_handler(CommandHandler("start", user_handlers[0].callback))
    
    # هندلر برای پیام‌های متنی معمولی
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_regular_message))
    
    # شروع ربات
    logger.info("🤖 Bot is starting...")
    await application.run_polling()

async def handle_regular_message(update, context):
    """پردازش پیام‌های متنی معمولی"""
    user_id = update.message.from_user.id
    
    # اگر کاربر در حال آپلود رسید است، از هندلر مخصوص استفاده کن
    if update.message.photo or update.message.document:
        return
    
    # در غیر این صورت کاربر را به منوی اصلی هدایت کن
    from handlers.user_handlers import start
    await start(update, context)

if __name__ == "__main__":
    asyncio.run(main())

import os
import asyncio
import logging
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from database import db

# تنظیمات logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# لود متغیرهای محیطی
load_dotenv()

async def start(update, context):
    """دستور شروع ربات"""
    user = update.effective_user
    user_id = user.id
    
    # ایجاد کاربر در دیتابیس
    await db.create_user(user_id, user.username, user.first_name, user.last_name or "")
    await db.add_log(user_id, "start", "کاربر ربات را شروع کرد")
    
    welcome_text = """
🤖 به ربات فروش VPN خوش آمدید!

🔒 با استفاده از این ربات می‌توانید:
• VPN پرسرعت خریداری کنید
• سفارشات خود را مدیریت کنید
• موجودی کیف پول خود را بررسی کنید

برای شروع از دکمه‌های زیر استفاده کنید:
"""
    
    from utils.helpers import get_main_keyboard, is_admin
    keyboard = get_main_keyboard(is_admin(user_id))
    
    if update.callback_query:
        await update.callback_query.edit_message_text(welcome_text, reply_markup=keyboard)
    else:
        await update.message.reply_text(welcome_text, reply_markup=keyboard)

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
    
    # اضافه کردن هندلرها
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(start, pattern="^main_menu$"))
    
    # اضافه کردن سایر هندلرها از ماژول‌ها
    from handlers.user_handlers import user_handlers
    from handlers.admin_handlers import admin_handlers
    
    for handler in user_handlers:
        application.add_handler(handler)
    
    for handler in admin_handlers:
        application.add_handler(handler)
    
    # هندلر برای پیام‌های متنی معمولی
    async def handle_regular_message(update, context):
        """پردازش پیام‌های متنی معمولی"""
        user_id = update.message.from_user.id
        
        # اگر کاربر در حال آپلود رسید است، از هندلر مخصوص استفاده کن
        if update.message.photo or update.message.document:
            return
        
        # در غیر این صورت کاربر را به منوی اصلی هدایت کن
        await start(update, context)
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_regular_message))
    
    # شروع ربات
    logger.info("🤖 Bot is starting...")
    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())

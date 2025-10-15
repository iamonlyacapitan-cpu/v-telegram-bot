import os
import logging
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from database import db
from handlers.user_handlers import user_handlers
from handlers.admin_handlers import admin_handlers
from utils.helpers import is_admin

# تنظیمات logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

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
    
    from utils.helpers import get_main_keyboard
    keyboard = get_main_keyboard(is_admin(user_id))
    
    if update.callback_query:
        await update.callback_query.edit_message_text(welcome_text, reply_markup=keyboard)
    else:
        await update.message.reply_text(welcome_text, reply_markup=keyboard)

def main():
    """تابع اصلی اجرای ربات"""
    # ایجاد اپلیکیشن
    bot_token = os.getenv('BOT_TOKEN')
    if not bot_token:
        logger.error("❌ BOT_TOKEN not found in environment variables")
        return
    
    updater = Updater(bot_token, use_context=True)
    dispatcher = updater.dispatcher

    # اضافه کردن هندلر شروع
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(start, pattern="^main_menu$"))
    
    # اضافه کردن هندلرهای کاربران
    for handler in user_handlers:
        dispatcher.add_handler(handler)
    
    # اضافه کردن هندلرهای ادمین
    for handler in admin_handlers:
        dispatcher.add_handler(handler)
    
    # هندلر برای پیام‌های متنی معمولی
    def handle_regular_message(update, context):
        """پردازش پیام‌های متنی معمولی"""
        user_id = update.message.from_user.id
        
        # اگر کاربر در حال آپلود رسید است، از هندلر مخصوص استفاده کن
        if update.message.photo or update.message.document:
            return
        
        # در غیر این صورت کاربر را به منوی اصلی هدایت کن
        start(update, context)
    
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_regular_message))
    
    # شروع ربات
    logger.info("🤖 Bot is starting...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    # اتصال به دیتابیس و سپس اجرای ربات
    import asyncio
    asyncio.run(db.connect())
    main()

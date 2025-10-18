import os
import asyncio
import logging
import sys

# اضافه کردن مسیر فعلی به Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

# Import از ماژول‌های داخلی
from app.config import config
from app.database.repository import DatabaseRepository
from app.handlers.user_handlers import UserHandlers
from app.handlers.admin_handlers import AdminHandlers
from app.handlers.admin_management import AdminManagementHandlers

# تنظیمات لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def main():
    """تابع اصلی اجرای ربات"""
    
    try:
        # راه‌اندازی دیتابیس
        db = DatabaseRepository(config.DATABASE_URL)
        await db.connect()
        
        # ایجاد application
        application = Application.builder().token(config.BOT_TOKEN).build()
        
        # ذخیره دیتابیس در bot_data
        application.bot_data['db'] = db
        
        # ایجاد هندلرها
        user_handlers = UserHandlers(db)
        admin_handlers = AdminHandlers(db)
        admin_management = AdminManagementHandlers(db)
        
        # ثبت هندلرها
        # دستورات کاربران
        application.add_handler(CommandHandler("start", user_handlers.start))
        application.add_handler(CommandHandler("profile", user_handlers.profile))
        
        # Callback queries کاربران
        application.add_handler(CallbackQueryHandler(user_handlers.start, pattern="^main_menu$"))
        application.add_handler(CallbackQueryHandler(user_handlers.show_plans, pattern="^buy_vpn$"))
        application.add_handler(CallbackQueryHandler(user_handlers.select_plan, pattern="^plan_"))
        
        # مدیریت رسید پرداخت
        application.add_handler(MessageHandler(
            filters.PHOTO, 
            user_handlers.handle_payment_receipt
        ))
        
        # هندلرهای ادمین
        application.add_handler(CommandHandler("admin", admin_handlers.admin_panel))
        application.add_handler(CallbackQueryHandler(admin_handlers.manage_orders, pattern="^admin_orders$"))
        application.add_handler(CallbackQueryHandler(admin_handlers.send_config_text, pattern="^config_text_"))
        
        # مدیریت ادمین‌ها
        application.add_handler(CallbackQueryHandler(admin_management.manage_admins, pattern="^admin_management$"))
        application.add_handler(CallbackQueryHandler(admin_management.add_admin, pattern="^add_admin$"))
        
        # هندلرهای متن برای ادمین
        application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, 
            admin_management.handle_admin_info
        ))
        application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, 
            admin_handlers.handle_config_text
        ))
        
        # هندلر بازگشت
        application.add_handler(CallbackQueryHandler(admin_handlers.admin_panel, pattern="^admin_back$"))
        
        # شروع ربات
        logger.info("✅ Bot starting...")
        await application.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

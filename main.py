import os
import asyncio
import logging
import sys
import signal

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

class TelegramBot:
    def __init__(self):
        self.application = None
        self.db = None
    
    async def initialize(self):
        """مقداردهی اولیه ربات"""
        try:
            # راه‌اندازی دیتابیس
            self.db = DatabaseRepository(config.DATABASE_URL)
            await self.db.connect()
            
            # ایجاد application
            self.application = Application.builder().token(config.BOT_TOKEN).build()
            
            # ذخیره دیتابیس در bot_data
            self.application.bot_data['db'] = self.db
            
            # ایجاد و ثبت هندلرها
            await self._setup_handlers()
            
            logger.info("✅ Bot initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize bot: {e}")
            return False
    
    async def _setup_handlers(self):
        """تنظیم هندلرها"""
        user_handlers = UserHandlers(self.db)
        admin_handlers = AdminHandlers(self.db)
        admin_management = AdminManagementHandlers(self.db)
        
        # دستورات کاربران
        self.application.add_handler(CommandHandler("start", user_handlers.start))
        self.application.add_handler(CommandHandler("profile", user_handlers.profile))
        self.application.add_handler(CommandHandler("help", user_handlers.help_command))
        
        # Callback queries کاربران
        self.application.add_handler(CallbackQueryHandler(user_handlers.start, pattern="^main_menu$"))
        self.application.add_handler(CallbackQueryHandler(user_handlers.show_plans, pattern="^buy_vpn$"))
        self.application.add_handler(CallbackQueryHandler(user_handlers.select_plan, pattern="^plan_"))
        self.application.add_handler(CallbackQueryHandler(user_handlers.profile, pattern="^order_history$"))
        
        # مدیریت رسید پرداخت
        self.application.add_handler(MessageHandler(
            filters.PHOTO, 
            user_handlers.handle_payment_receipt
        ))
        
        # هندلرهای ادمین
        self.application.add_handler(CommandHandler("admin", admin_handlers.admin_panel))
        self.application.add_handler(CallbackQueryHandler(admin_handlers.manage_orders, pattern="^admin_orders$"))
        self.application.add_handler(CallbackQueryHandler(admin_handlers.send_config_text, pattern="^config_text_"))
        
        # مدیریت ادمین‌ها
        self.application.add_handler(CallbackQueryHandler(admin_management.manage_admins, pattern="^admin_management$"))
        self.application.add_handler(CallbackQueryHandler(admin_management.add_admin, pattern="^add_admin$"))
        
        # هندلرهای متن برای ادمین
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, 
            admin_management.handle_admin_info
        ))
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, 
            admin_handlers.handle_config_text
        ))
        
        # هندلر بازگشت
        self.application.add_handler(CallbackQueryHandler(admin_handlers.admin_panel, pattern="^admin_back$"))
    
    async def start(self):
        """شروع ربات"""
        if not self.application:
            logger.error("❌ Application not initialized")
            return
        
        try:
            await self.application.initialize()
            await self.application.start()
            logger.info("✅ Bot started successfully")
            
            # اجرای ربات تا زمانی که متوقف شود
            await self.application.updater.start_polling(
                drop_pending_updates=True,
                timeout=60,
                pool_timeout=60
            )
            
            # نگه داشتن ربات در حال اجرا
            await self._keep_alive()
            
        except Exception as e:
            logger.error(f"❌ Failed to start bot: {e}")
            raise
    
    async def _keep_alive(self):
        """نگه داشتن ربات در حال اجرا"""
        try:
            while True:
                await asyncio.sleep(3600)  # هر 1 ساعت چک کن
        except asyncio.CancelledError:
            logger.info("🛑 Bot stopping...")
    
    async def stop(self):
        """توقف ربات"""
        if self.application:
            await self.application.stop()
            await self.application.shutdown()
        logger.info("✅ Bot stopped successfully")

# ایجاد global instance
bot = TelegramBot()

async def main():
    """تابع اصلی"""
    try:
        # مقداردهی اولیه
        if not await bot.initialize():
            sys.exit(1)
        
        # شروع ربات
        await bot.start()
        
    except KeyboardInterrupt:
        logger.info("🛑 Received interrupt signal")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
    finally:
        await bot.stop()

def handler(signum, frame):
    """Handler برای signals"""
    logger.info(f"📞 Received signal {signum}")
    asyncio.create_task(bot.stop())

if __name__ == "__main__":
    # ثبت signal handlers
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)
    
    # اجرای ربات
    asyncio.run(main())

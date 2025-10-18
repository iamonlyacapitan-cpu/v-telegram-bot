import os
import logging
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# تنظیمات logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class BotManager:
    def __init__(self):
        self.token = os.environ.get('BOT_TOKEN')
        self.updater = None
        
    def get_main_keyboard(self):
        keyboard = [
            [InlineKeyboardButton("🛒 خرید VPN", callback_data="buy_vpn")],
            [InlineKeyboardButton("ℹ️ راهنما", callback_data="help")],
            [InlineKeyboardButton("👨‍💼 پشتیبانی", url="https://t.me/username")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def start(self, update, context):
        user = update.effective_user
        welcome_text = f"""
🤖 سلام {user.first_name}!

به ربات فروش VPN خوش آمدید.

✅ **ربات با موفقیت فعال شد**

برای شروع از منوی زیر استفاده کنید:
"""
        
        if update.callback_query:
            update.callback_query.edit_message_text(welcome_text, reply_markup=self.get_main_keyboard())
        else:
            update.message.reply_text(welcome_text, reply_markup=self.get_main_keyboard())
    
    def show_plans(self, update, context):
        query = update.callback_query
        query.answer()
        
        plans_text = """
📦 **پلن‌های موجود:**

• پلن یک ماهه - 29,000 تومان
• پلن سه ماهه - 79,000 تومان  
• پلن یک ساله - 199,000 تومان

💳 **برای خرید:**
@username
"""
        keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")]]
        query.edit_message_text(plans_text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    def help_command(self, update, context):
        query = update.callback_query
        query.answer()
        
        help_text = """
📖 **راهنمای استفاده**

برای خرید VPN:
1. روی «خرید VPN» کلیک کنید
2. با پشتیبانی تماس بگیرید
3. پلن مورد نظر را انتخاب کنید

📞 پشتیبانی: @username
"""
        keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")]]
        query.edit_message_text(help_text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    def setup_handlers(self):
        """تنظیم هندلرها"""
        dispatcher = self.updater.dispatcher
        dispatcher.add_handler(CommandHandler("start", self.start))
        dispatcher.add_handler(CallbackQueryHandler(self.start, pattern="^main_menu$"))
        dispatcher.add_handler(CallbackQueryHandler(self.show_plans, pattern="^buy_vpn$"))
        dispatcher.add_handler(CallbackQueryHandler(self.help_command, pattern="^help$"))
    
    def run(self):
        """اجرای ربات"""
        if not self.token:
            logger.error("❌ BOT_TOKEN not found")
            return False
            
        try:
            self.updater = Updater(self.token, use_context=True)
            self.setup_handlers()
            
            logger.info("🚀 Starting bot on Render...")
            self.updater.start_polling()
            logger.info("✅ Bot started successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start bot: {e}")
            return False

def main():
    """تابع اصلی"""
    bot = BotManager()
    success = bot.run()
    
    if success:
        # نگه داشتن برنامه در حال اجرا
        bot.updater.idle()
    else:
        logger.error("❌ Bot failed to start")

if __name__ == "__main__":
    main()

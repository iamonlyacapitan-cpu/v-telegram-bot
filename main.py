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

class VPNBot:
    def __init__(self):
        self.token = os.environ.get('BOT_TOKEN')
        self.updater = None
    
    def get_main_keyboard(self):
        keyboard = [
            [InlineKeyboardButton("🛒 خرید VPN", callback_data="buy_vpn")],
            [InlineKeyboardButton("💰 قیمت‌ها", callback_data="prices")],
            [InlineKeyboardButton("ℹ️ راهنما", callback_data="help")],
            [InlineKeyboardButton("👨‍💼 پشتیبانی", callback_data="support")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def start(self, update, context):
        user = update.effective_user
        welcome_text = f"""
🤖 سلام {user.first_name}!

به **ربات فروش VPN** خوش آمدید.

✅ **ربات با موفقیت فعال شد**
🆔 شناسه شما: {user.id}

🔒 **خدمات ما:**
• VPN پرسرعت
• اتصال بدون قطعی  
• پشتیبانی ۲۴ ساعته

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
🛒 **پلن‌های VPN:**

📦 **پلن یک ماهه**
💰 قیمت: ۲۹,۰۰۰ تومان
⏰ مدت: ۳۰ روز
⚡ سرعت: نامحدود

📦 **پلن سه ماهه**  
💰 قیمت: ۷۹,۰۰۰ تومان
⏰ مدت: ۹۰ روز
⚡ سرعت: نامحدود

📦 **پلن یک ساله**
💰 قیمت: ۱۹۹,۰۰۰ تومان  
⏰ مدت: ۳۶۵ روز
⚡ سرعت: نامحدود

💳 **برای خرید با پشتیبانی تماس بگیرید:**
@admin
"""
        keyboard = [
            [InlineKeyboardButton("🔙 بازگشت به منو", callback_data="main_menu")]
        ]
        query.edit_message_text(plans_text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    def show_prices(self, update, context):
        query = update.callback_query
        query.answer()
        
        prices_text = """
💰 **لیست قیمت‌ها:**

• پلن یک ماهه: ۲۹,۰۰۰ تومان
• پلن سه ماهه: ۷۹,۰۰۰ تومان  
• پلن یک ساله: ۱۹۹,۰۰۰ تومان

💎 **تخفیف‌های ویژه برای خریدهای حجمی**
"""
        keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")]]
        query.edit_message_text(prices_text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    def help_command(self, update, context):
        query = update.callback_query
        query.answer()
        
        help_text = """
📖 **راهنمای استفاده**

🛒 **مراحل خرید:**
1. از منوی اصلی «خرید VPN» را انتخاب کنید
2. پلن مورد نظر خود را مشاهده کنید
3. با پشتیبانی تماس بگیرید
4. مبلغ را واریز کنید
5. کانفیگ را دریافت کنید

🔧 **نحوه استفاده:**
1. نصب برنامه OpenVPN
2. وارد کردن کانفیگ
3. اتصال به سرور

📞 **پشتیبانی:**
@admin
"""
        keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")]]
        query.edit_message_text(help_text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    def support_info(self, update, context):
        query = update.callback_query
        query.answer()
        
        support_text = """
👨‍💼 **پشتیبانی فنی**

📞 **تماس با پشتیبانی:**
@admin

🕒 **ساعات کاری:**
۲۴ ساعته

🔧 **خدمات پشتیبانی:**
• راهنمای نصب و تنظیم
• رفع مشکلات اتصال
• پاسخ به سوالات فنی
• پیگیری سفارشات
"""
        keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")]]
        query.edit_message_text(support_text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    def setup_handlers(self):
        """تنظیم هندلرها"""
        dispatcher = self.updater.dispatcher
        dispatcher.add_handler(CommandHandler("start", self.start))
        dispatcher.add_handler(CallbackQueryHandler(self.start, pattern="^main_menu$"))
        dispatcher.add_handler(CallbackQueryHandler(self.show_plans, pattern="^buy_vpn$"))
        dispatcher.add_handler(CallbackQueryHandler(self.show_prices, pattern="^prices$"))
        dispatcher.add_handler(CallbackQueryHandler(self.help_command, pattern="^help$"))
        dispatcher.add_handler(CallbackQueryHandler(self.support_info, pattern="^support$"))
    
    def run(self):
        """اجرای ربات"""
        if not self.token:
            logger.error("❌ BOT_TOKEN not found in environment variables")
            return False
            
        try:
            # ایجاد updater (نسخه قدیمی PTB)
            self.updater = Updater(self.token, use_context=True)
            self.setup_handlers()
            
            # شروع ربات
            logger.info("🚀 Starting VPN Bot with PTB 13.15...")
            self.updater.start_polling()
            logger.info("✅ Bot started successfully!")
            
            # نگه داشتن برنامه در حال اجرا
            self.updater.idle()
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start bot: {e}")
            return False

def main():
    """تابع اصلی"""
    bot = VPNBot()
    
    logger.info("🤖 Initializing VPN Bot...")
    logger.info(f"📝 Python version: 3.11 (Docker)")
    logger.info(f"📦 PTB version: 13.15")
    logger.info(f"🔑 Token: {'Found' if bot.token else 'Not Found'}")
    
    success = bot.run()
    
    if not success:
        logger.error("❌ Bot failed to start. Check the logs above.")

if __name__ == "__main__":
    main()

import os
import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
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
        self.application = None
    
    def get_main_keyboard(self):
        keyboard = [
            [InlineKeyboardButton("🛒 خرید VPN", callback_data="buy_vpn")],
            [InlineKeyboardButton("💰 قیمت‌ها", callback_data="prices")],
            [InlineKeyboardButton("ℹ️ راهنما", callback_data="help")],
            [InlineKeyboardButton("👨‍💼 پشتیبانی", callback_data="support")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    async def start(self, update, context):
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
            await update.callback_query.edit_message_text(welcome_text, reply_markup=self.get_main_keyboard())
        else:
            await update.message.reply_text(welcome_text, reply_markup=self.get_main_keyboard())
    
    async def show_plans(self, update, context):
        query = update.callback_query
        await query.answer()
        
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
🎁 تخفیف: ۱۰٪

📦 **پلن یک ساله**
💰 قیمت: ۱۹۹,۰۰۰ تومان  
⏰ مدت: ۳۶۵ روز
⚡ سرعت: نامحدود
🎁 تخفیف: ۳۰٪

💳 **برای خرید:**
لطفا با پشتیبانی تماس بگیرید 👇
"""
        keyboard = [
            [InlineKeyboardButton("👨‍💼 تماس با پشتیبانی", url="https://t.me/username")],
            [InlineKeyboardButton("🔙 بازگشت به منو", callback_data="main_menu")]
        ]
        await query.edit_message_text(plans_text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def show_prices(self, update, context):
        query = update.callback_query
        await query.answer()
        
        prices_text = """
💰 **لیست قیمت‌ها:**

• پلن یک ماهه: ۲۹,۰۰۰ تومان
• پلن سه ماهه: ۷۹,۰۰۰ تومان
• پلن شش ماهه: ۱۴۹,۰۰۰ تومان
• پلن یک ساله: ۱۹۹,۰۰۰ تومان

💎 **پلن ویژه:**
• پلن دائمی: ۴۹۹,۰۰۰ تومان

🎁 **تخفیف‌های حجمی موجود**
"""
        keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")]]
        await query.edit_message_text(prices_text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def help_command(self, update, context):
        query = update.callback_query
        await query.answer()
        
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
۲۴ ساعته در ۷ روز هفته
"""
        keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")]]
        await query.edit_message_text(help_text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def support_info(self, update, context):
        query = update.callback_query
        await query.answer()
        
        support_text = """
👨‍💼 **پشتیبانی فنی**

📞 **تماس با پشتیبانی:**
@username

🕒 **ساعات کاری:**
۲۴ ساعته

🔧 **خدمات پشتیبانی:**
• راهنمای نصب و تنظیم
• رفع مشکلات اتصال
• پاسخ به سوالات فنی
• پیگیری سفارشات

💬 **لطفا در تماس:**
• شماره کاربری خود را mention کنید
• مشکل را به طور کامل شرح دهید
"""
        keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")]]
        await query.edit_message_text(support_text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    def setup_handlers(self):
        """تنظیم هندلرها"""
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CallbackQueryHandler(self.start, pattern="^main_menu$"))
        self.application.add_handler(CallbackQueryHandler(self.show_plans, pattern="^buy_vpn$"))
        self.application.add_handler(CallbackQueryHandler(self.show_prices, pattern="^prices$"))
        self.application.add_handler(CallbackQueryHandler(self.help_command, pattern="^help$"))
        self.application.add_handler(CallbackQueryHandler(self.support_info, pattern="^support$"))
    
    def run(self):
        """اجرای ربات"""
        if not self.token:
            logger.error("❌ BOT_TOKEN not found in environment variables")
            return False
            
        try:
            # ایجاد اپلیکیشن
            self.application = Application.builder().token(self.token).build()
            self.setup_handlers()
            
            # شروع ربات
            logger.info("🚀 Starting VPN Bot with Docker...")
            self.application.run_polling()
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start bot: {e}")
            return False

def main():
    """تابع اصلی"""
    bot = VPNBot()
    
    logger.info("🤖 Initializing VPN Bot...")
    logger.info(f"📝 Python version: 3.11 (Docker)")
    logger.info(f"🔑 Token: {'Found' if bot.token else 'Not Found'}")
    
    bot.run()

if __name__ == "__main__":
    main()

import os
import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# تنظیمات logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def get_main_keyboard():
    """کیبورد اصلی"""
    keyboard = [
        [InlineKeyboardButton("🛒 خرید VPN", callback_data="buy_vpn")],
        [InlineKeyboardButton("💰 کیف پول", callback_data="wallet")],
        [InlineKeyboardButton("ℹ️ راهنما", callback_data="help")],
        [InlineKeyboardButton("👨‍💼 پشتیبانی", callback_data="support")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور شروع ربات"""
    user = update.effective_user
    
    welcome_text = f"""
🤖 سلام {user.first_name}! به ربات فروش VPN خوش آمدید!

🔒 **خدمات ما:**
• VPN پرسرعت و مطمئن
• پشتیبانی 24 ساعته
• قیمت‌های رقابتی

🎯 **پلن‌های موجود:**
📦 پلن یک ماهه - 29,000 تومان
📦 پلن سه ماهه - 79,000 تومان  
📦 پلن یک ساله - 199,000 تومان

برای شروع از دکمه‌های زیر استفاده کنید:
"""
    
    keyboard = get_main_keyboard()
    
    if update.callback_query:
        await update.callback_query.edit_message_text(welcome_text, reply_markup=keyboard)
    else:
        await update.message.reply_text(welcome_text, reply_markup=keyboard)

async def show_plans(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش پلن‌ها"""
    query = update.callback_query
    await query.answer()
    
    plans_text = """
🛒 **پلن‌های VPN:**

📦 **پلن یک ماهه**
💰 29,000 تومان
⏰ 30 روز دسترسی
⚡ سرعت نامحدود

📦 **پلن سه ماهه**  
💰 79,000 تومان
⏰ 90 روز دسترسی
⚡ سرعت نامحدود
🎁 10% تخفیف

📦 **پلن یک ساله**
💰 199,000 تومان  
⏰ 365 روز دسترسی
⚡ سرعت نامحدود
🎁 30% تخفیف

💳 **روش خرید:**
1. پلن مورد نظر را انتخاب کنید
2. مبلغ را به شماره کارت زیر واریز کنید:
   🏦 بانک: ملت
   💳 6104-3378-1234-5678
3. رسید پرداخت را برای @admin ارسال کنید
4. کانفیگ VPN را دریافت کنید
"""
    
    keyboard = [[InlineKeyboardButton("🔙 بازگشت به منو", callback_data="main_menu")]]
    await query.edit_message_text(plans_text, reply_markup=InlineKeyboardMarkup(keyboard))

async def wallet_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """اطلاعات کیف پول"""
    query = update.callback_query
    await query.answer()
    
    wallet_text = """
💰 **سیستم کیف پول**

💵 **روش‌های شارژ:**
• واریز به شماره کارت
• پرداخت آنلاین
• رمزارز (بیت‌کوین)

🏦 **شماره کارت:**
6104-3378-1234-5678
بانک ملت
به نام: جان دون

📞 **پس از واریز:**
رسید پرداخت را برای @admin ارسال کنید
"""
    
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")]]
    await query.edit_message_text(wallet_text, reply_markup=InlineKeyboardMarkup(keyboard))

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """راهنما"""
    query = update.callback_query
    await query.answer()
    
    help_text = """
ℹ️ **راهنمای استفاده**

🛒 **خرید VPN:**
1. از منوی اصلی گزینه «خرید VPN» را انتخاب کنید
2. پلن مورد نظر خود را انتخاب کنید
3. مبلغ را واریز کنید
4. رسید را برای پشتیبانی ارسال کنید

🔧 **نحوه استفاده از کانفیگ:**
1. اپلیکیشن OpenVPN را نصب کنید
2. فایل کانفیگ را import کنید
3. به سرور متصل شوید

📞 **پشتیبانی:**
@admin
🕒 24 ساعته
"""
    
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")]]
    await query.edit_message_text(help_text, reply_markup=InlineKeyboardMarkup(keyboard))

async def support_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """اطلاعات پشتیبانی"""
    query = update.callback_query
    await query.answer()
    
    support_text = """
👨‍💼 **پشتیبانی فنی**

📞 **تماس با پشتیبانی:**
@admin

🕒 **ساعات پاسخگویی:**
24 ساعته، 7 روز هفته

🔧 **خدمات پشتیبانی:**
• راهنمای نصب و استفاده
• حل مشکلات اتصال
• تمدید سرویس
• پاسخ به سوالات فنی

💬 **لطفا برای سریع‌تر شدن فرآیند:**
• شماره سفارش خود را ذکر کنید
• مشکل خود را به طور کامل شرح دهید
• عکس خطا (اگر وجود دارد) ارسال کنید
"""
    
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")]]
    await query.edit_message_text(support_text, reply_markup=InlineKeyboardMarkup(keyboard))

def main():
    """تابع اصلی"""
    try:
        # ایجاد اپلیکیشن
        BOT_TOKEN = os.getenv('BOT_TOKEN', '8462720172:AAG4qi1g8tz87NiMU7moM0c3k8SztZ5WAw4')
        
        application = Application.builder().token(BOT_TOKEN).build()
        
        # اضافه کردن هندلرها
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CallbackQueryHandler(start, pattern="^main_menu$"))
        application.add_handler(CallbackQueryHandler(show_plans, pattern="^buy_vpn$"))
        application.add_handler(CallbackQueryHandler(wallet_info, pattern="^wallet$"))
        application.add_handler(CallbackQueryHandler(help_command, pattern="^help$"))
        application.add_handler(CallbackQueryHandler(support_info, pattern="^support$"))
        
        # شروع ربات
        logger.info("🤖 Bot is starting (Simple Version)...")
        application.run_polling()
        
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")

if __name__ == "__main__":
    main()

import os
import logging
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("🛒 خرید VPN", callback_data="buy_vpn")],
        [InlineKeyboardButton("ℹ️ راهنما", callback_data="help")]
    ]
    return InlineKeyboardMarkup(keyboard)

def start(update, context):
    user = update.effective_user
    update.message.reply_text(
        f"✅ ربات فعال شد! سلام {user.first_name}\n\n"
        "از منوی زیر انتخاب کنید:",
        reply_markup=get_main_keyboard()
    )

def main():
    BOT_TOKEN = os.environ.get('BOT_TOKEN')
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN not found")
        return
    
    updater = Updater(BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    
    # اضافه کردن هندلرها
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("test", start))
    
    # استفاده از polling با تنظیمات بهتر
    logger.info("🚀 Starting bot with optimized polling...")
    
    try:
        updater.start_polling(
            poll_interval=1.0,
            timeout=20,
            read_latency=2.0
        )
        logger.info("✅ Bot polling started!")
        
        # تست ارسال پیام
        logger.info("🤖 Bot is ready and waiting for messages...")
        
        updater.idle()
        
    except Exception as e:
        logger.error(f"❌ Polling error: {e}")

if __name__ == "__main__":
    main()

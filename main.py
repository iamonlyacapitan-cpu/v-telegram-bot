import os
import logging
from telegram.ext import Updater, CommandHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def start(update, context):
    user = update.effective_user
    update.message.reply_text(
        f"🎉 **ربات کاملاً جدید فعال شد!**\n"
        f"سلام {user.first_name}!\n\n"
        f"🆔 شناسه شما: {user.id}\n"
        f"✅ این یک instance جدید است\n"
        f"🚀 بدون conflict"
    )

def main():
    # توکن جدید رو اینجا قرار دهید
    BOT_TOKEN = os.environ.get('8462720172:AAHichJLgiyOJfRWoN6a_WX9ep-oem5kZvU')
    
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN not found")
        return
    
    logger.info("🆕 Starting FRESH bot instance...")
    
    try:
        updater = Updater(BOT_TOKEN, use_context=True)
        dispatcher = updater.dispatcher
        
        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(CommandHandler("ping", start))
        
        # شروع با drop_pending_updates برای پاک کردن صف قدیمی
        updater.start_polling(drop_pending_updates=True)
        
        logger.info("✅ FRESH bot started successfully!")
        logger.info("🤖 Bot is ready and waiting...")
        
        updater.idle()
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")

if __name__ == "__main__":
    main()

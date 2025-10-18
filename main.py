import os
import logging
from telegram.ext import Updater, CommandHandler

# تنظیمات logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def start(update, context):
    user = update.effective_user
    update.message.reply_text(f"✅ ربات فعال شد! سلام {user.first_name}")

def main():
    # دریافت توکن از environment variables
    BOT_TOKEN = os.environ.get('BOT_TOKEN')
    
    # خطایابی دقیق
    logger.info("🔍 Checking environment variables...")
    logger.info(f"BOT_TOKEN exists: {bool(BOT_TOKEN)}")
    logger.info(f"BOT_TOKEN value: {BOT_TOKEN[:10] + '...' if BOT_TOKEN else 'NOT FOUND'}")
    
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN not found in environment variables")
        logger.error("💡 Please set BOT_TOKEN in Render Environment Variables")
        return
    
    try:
        logger.info("🚀 Starting bot...")
        updater = Updater(BOT_TOKEN, use_context=True)
        dispatcher = updater.dispatcher
        
        dispatcher.add_handler(CommandHandler("start", start))
        
        logger.info("✅ Bot initialized successfully!")
        updater.start_polling()
        logger.info("🔄 Bot started polling...")
        
        updater.idle()
        
    except Exception as e:
        logger.error(f"❌ Error starting bot: {e}")

if __name__ == "__main__":
    main()

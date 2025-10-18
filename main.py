import os
import logging
from telegram.ext import Updater, CommandHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def start(update, context):
    user = update.effective_user
    update.message.reply_text(f"✅ ربات فعال شد! سلام {user.first_name}")

def main():
    BOT_TOKEN = os.environ.get('BOT_TOKEN')
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN not found")
        return
    
    updater = Updater(BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    
    logger.info("🚀 Starting bot...")
    updater.start_polling()
    logger.info("✅ Bot started successfully!")
    updater.idle()

if __name__ == "__main__":
    main()

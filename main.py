import os
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Health Check Server
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        return

def start_health_server():
    port = int(os.environ.get('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    logger.info(f"🩺 Health server on port {port}")
    server.serve_forever()

def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("🛒 خرید VPN", callback_data="buy_vpn")],
        [InlineKeyboardButton("💰 قیمت‌ها", callback_data="prices")],
        [InlineKeyboardButton("ℹ️ راهنما", callback_data="help")],
        [InlineKeyboardButton("👨‍💼 پشتیبانی", callback_data="support")]
    ]
    return InlineKeyboardMarkup(keyboard)

def start(update, context):
    user = update.effective_user
    message = (
        f"🎉 **ربات VPN کاملاً جدید فعال شد!**\n\n"
        f"👋 سلام {user.first_name}!\n"
        f"🆔 شناسه شما: {user.id}\n"
        f"✅ Instance: کاملاً جدید\n"
        f"🚀 وضعیت: بدون Conflict\n\n"
        f"برای شروع از منوی زیر استفاده کنید:"
    )
    
    if update.callback_query:
        update.callback_query.edit_message_text(message, reply_markup=get_main_keyboard())
    else:
        update.message.reply_text(message, reply_markup=get_main_keyboard())

def show_plans(update, context):
    query = update.callback_query
    query.answer()
    
    plans_text = """
📦 **پلن‌های VPN:**

• یک ماهه - 29,000 تومان
• سه ماهه - 79,000 تومان  
• یک ساله - 199,000 تومان

💳 برای خرید با پشتیبانی تماس بگیرید.
"""
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")]]
    query.edit_message_text(plans_text, reply_markup=InlineKeyboardMarkup(keyboard))

def main():
    # توکن ربات جدید رو اینجا قرار دهید
    BOT_TOKEN = os.environ.get('BOT_TOKEN')
    
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN not found")
        return
    
    logger.info("🆕 Starting COMPLETELY NEW bot...")
    logger.info(f"🔑 Token: {BOT_TOKEN[:15]}...")
    
    # شروع health server
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()
    
    try:
        # ایجاد ربات جدید
        updater = Updater(BOT_TOKEN, use_context=True)
        dispatcher = updater.dispatcher
        
        # اضافه کردن هندلرها
        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(CommandHandler("test", start))
        dispatcher.add_handler(CallbackQueryHandler(start, pattern="^main_menu$"))
        dispatcher.add_handler(CallbackQueryHandler(show_plans, pattern="^buy_vpn$"))
        
        # شروع ربات با تنظیمات ویژه
        updater.start_polling(
            drop_pending_updates=True,
            poll_interval=0.5,
            timeout=10,
            read_latency=2.0
        )
        
        logger.info("✅ COMPLETELY NEW bot started successfully!")
        logger.info("🤖 Bot is ready and waiting for /start command...")
        
        # نگه داشتن برنامه
        updater.idle()
        
    except Exception as e:
        logger.error(f"❌ Error starting new bot: {e}")

if __name__ == "__main__":
    main()

import os
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram.ext import Updater, CommandHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

def start(update, context):
    user = update.effective_user
    update.message.reply_text(
        f"🎉 **ربات کاملاً جدید فعال شد!**\n"
        f"سلام {user.first_name}!\n\n"
        f"✅ بدون conflict\n"
        f"🚀 روی Render اجرا شده\n"
        f"🆔 شناسه شما: {user.id}"
    )

def main():
    BOT_TOKEN = os.environ.get('BOT_TOKEN')
    
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN not found")
        return
    
    # شروع health server
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()
    
    try:
        logger.info("🆕 Starting FRESH bot instance...")
        
        # استفاده از drop_pending_updates برای پاک کردن صف قدیمی
        updater = Updater(BOT_TOKEN, use_context=True)
        dispatcher = updater.dispatcher
        
        dispatcher.add_handler(CommandHandler("start", start))
        
        # شروع با drop_pending_updates=True
        updater.start_polling(
            drop_pending_updates=True,
            poll_interval=1.0,
            timeout=20
        )
        
        logger.info("✅ FRESH bot started successfully!")
        logger.info("🤖 Waiting for /start command...")
        
        updater.idle()
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")

if __name__ == "__main__":
    main()

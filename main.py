import os
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram.ext import Updater, CommandHandler

# تنظیمات logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Health Check Server
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        logger.info(f"Health check: {format % args}")

def start_health_server():
    """شروع سرور health check روی پورت 8080"""
    port = int(os.environ.get('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    logger.info(f"🩺 Health check server started on port {port}")
    server.serve_forever()

def start(update, context):
    """دستور شروع"""
    user = update.effective_user
    update.message.reply_text(
        f"✅ ربات فعال شد! سلام {user.first_name}\n\n"
        f"🆔 شناسه شما: {user.id}\n"
        f"🌐 Health check: فعال"
    )

def main():
    # دریافت توکن
    BOT_TOKEN = os.environ.get('BOT_TOKEN')
    
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN not found")
        return
    
    # شروع health server در thread جداگانه
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()
    
    try:
        logger.info("🚀 Starting Telegram bot...")
        updater = Updater(BOT_TOKEN, use_context=True)
        dispatcher = updater.dispatcher
        
        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(CommandHandler("ping", start))
        
        # شروع ربات
        updater.start_polling()
        logger.info("✅ Telegram bot started successfully!")
        logger.info("🤖 Bot is ready and waiting for messages...")
        
        # نگه داشتن برنامه
        updater.idle()
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")

if __name__ == "__main__":
    main()

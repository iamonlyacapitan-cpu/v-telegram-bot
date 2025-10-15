import os
import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
import psycopg2
from psycopg2.extras import RealDictCursor

# تنظیمات logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.conn = None
    
    def connect(self):
        """اتصال به دیتابیس"""
        try:
            self.conn = psycopg2.connect(
                os.getenv('DATABASE_URL'),
                cursor_factory=RealDictCursor
            )
            self.create_tables()
            logger.info("✅ Connected to database successfully")
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
    
    def create_tables(self):
        """ایجاد جداول مورد نیاز"""
        with self.conn.cursor() as cur:
            # جدول کاربران
            cur.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    is_admin BOOLEAN DEFAULT FALSE,
                    balance INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            ''')
            
            # جدول پلن‌ها
            cur.execute('''
                CREATE TABLE IF NOT EXISTS plans (
                    plan_id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    price INTEGER NOT NULL,
                    duration_days INTEGER NOT NULL,
                    description TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            ''')
            
            # ایجاد کاربر ادمین اصلی
            admin_id = int(os.getenv('ADMIN_ID'))
            cur.execute('''
                INSERT INTO users (user_id, is_admin, balance)
                VALUES (%s, TRUE, 0)
                ON CONFLICT (user_id) DO UPDATE SET is_admin = TRUE
            ''', (admin_id,))
            
            # ایجاد پلن‌های پیش‌فرض
            cur.execute('''
                INSERT INTO plans (name, price, duration_days, description) 
                VALUES 
                ('پلن یک ماهه', 29000, 30, 'دسترسی یک ماهه به VPN پرسرعت'),
                ('پلن سه ماهه', 79000, 90, 'دسترسی سه ماهه با قیمت ویژه'),
                ('پلن یک ساله', 199000, 365, 'دسترسی یک ساله با بهترین قیمت')
                ON CONFLICT DO NOTHING
            ''')
            
            self.conn.commit()
    
    def get_user(self, user_id: int):
        with self.conn.cursor() as cur:
            cur.execute('SELECT * FROM users WHERE user_id = %s', (user_id,))
            return cur.fetchone()
    
    def create_user(self, user_id: int, username: str, first_name: str, last_name: str = ""):
        with self.conn.cursor() as cur:
            cur.execute('''
                INSERT INTO users (user_id, username, first_name, last_name)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (user_id) DO NOTHING
            ''', (user_id, username, first_name, last_name))
            self.conn.commit()
    
    def get_plans(self):
        with self.conn.cursor() as cur:
            cur.execute('SELECT * FROM plans WHERE is_active = TRUE ORDER BY price')
            return cur.fetchall()

# ایجاد نمونه دیتابیس
db = Database()

def get_main_keyboard():
    """کیبورد اصلی"""
    keyboard = [
        [InlineKeyboardButton("🛒 خرید VPN", callback_data="buy_vpn")],
        [InlineKeyboardButton("📋 سفارشات من", callback_data="my_orders")],
        [InlineKeyboardButton("💰 کیف پول", callback_data="wallet")],
        [InlineKeyboardButton("ℹ️ راهنما", callback_data="help")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context):
    """دستور شروع ربات"""
    user = update.effective_user
    user_id = user.id
    
    # ایجاد کاربر در دیتابیس
    db.create_user(user_id, user.username, user.first_name, user.last_name or "")
    
    welcome_text = """
🤖 به ربات فروش VPN خوش آمدید!

🔒 با استفاده از این ربات می‌توانید:
• VPN پرسرعت خریداری کنید
• سفارشات خود را مدیریت کنید
• موجودی کیف پول خود را بررسی کنید

برای شروع از دکمه‌های زیر استفاده کنید:
"""
    
    keyboard = get_main_keyboard()
    
    if update.callback_query:
        await update.callback_query.edit_message_text(welcome_text, reply_markup=keyboard)
    else:
        await update.message.reply_text(welcome_text, reply_markup=keyboard)

async def show_plans(update: Update, context):
    """نمایش پلن‌ها"""
    query = update.callback_query
    await query.answer()
    
    plans = db.get_plans()
    
    plans_text = "🛒 پلن‌های موجود:\n\n"
    for plan in plans:
        plans_text += f"📦 {plan['name']}\n"
        plans_text += f"💰 قیمت: {plan['price']:,} تومان\n"
        plans_text += f"⏰ مدت: {plan['duration_days']} روز\n"
        plans_text += f"📝 {plan['description']}\n"
        plans_text += "─" * 30 + "\n"
    
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")]]
    await query.edit_message_text(plans_text, reply_markup=InlineKeyboardMarkup(keyboard))

async def help_command(update: Update, context):
    """راهنما"""
    query = update.callback_query
    await query.answer()
    
    help_text = """
ℹ️ راهنمای استفاده از ربات:

🛒 خرید VPN:
• از منوی اصلی گزینه خرید را انتخاب کنید
• پلن مورد نظر خود را انتخاب کنید
• با ادمین برای تکمیل خرید تماس بگیرید

📞 پشتیبانی:
@admin
"""
    
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")]]
    await query.edit_message_text(help_text, reply_markup=InlineKeyboardMarkup(keyboard))

def main():
    """تابع اصلی"""
    # اتصال به دیتابیس
    db.connect()
    
    # ایجاد اپلیکیشن
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    application = Application.builder().token(BOT_TOKEN).build()
    
    # اضافه کردن هندلرها
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(start, pattern="^main_menu$"))
    application.add_handler(CallbackQueryHandler(show_plans, pattern="^buy_vpn$"))
    application.add_handler(CallbackQueryHandler(help_command, pattern="^help$"))
    
    # شروع ربات
    logger.info("🤖 Bot is starting on Render...")
    application.run_polling()

if __name__ == "__main__":
    main()

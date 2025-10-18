import os
import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

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
            
            # جدول سفارشات
            cur.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    order_id SERIAL PRIMARY KEY,
                    user_id BIGINT REFERENCES users(user_id),
                    plan_id INTEGER REFERENCES plans(plan_id),
                    status TEXT DEFAULT 'pending',
                    payment_receipt TEXT,
                    vpn_config TEXT,
                    admin_note TEXT,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            ''')
            
            # جدول لاگ‌ها
            cur.execute('''
                CREATE TABLE IF NOT EXISTS logs (
                    log_id SERIAL PRIMARY KEY,
                    user_id BIGINT,
                    action TEXT,
                    details TEXT,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            ''')
            
            # ایجاد کاربر ادمین اصلی
            admin_id = int(os.getenv('ADMIN_ID', 1606291654))
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
            logger.info("✅ Database tables created successfully")
    
    def get_user(self, user_id: int):
        try:
            with self.conn.cursor() as cur:
                cur.execute('SELECT * FROM users WHERE user_id = %s', (user_id,))
                return cur.fetchone()
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
    
    def create_user(self, user_id: int, username: str, first_name: str, last_name: str = ""):
        try:
            with self.conn.cursor() as cur:
                cur.execute('''
                    INSERT INTO users (user_id, username, first_name, last_name)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (user_id) DO NOTHING
                ''', (user_id, username, first_name, last_name))
                self.conn.commit()
        except Exception as e:
            logger.error(f"Error creating user: {e}")
    
    def get_plans(self):
        try:
            with self.conn.cursor() as cur:
                cur.execute('SELECT * FROM plans WHERE is_active = TRUE ORDER BY price')
                return cur.fetchall()
        except Exception as e:
            logger.error(f"Error getting plans: {e}")
            return []
    
    def get_plan(self, plan_id: int):
        try:
            with self.conn.cursor() as cur:
                cur.execute('SELECT * FROM plans WHERE plan_id = %s', (plan_id,))
                return cur.fetchone()
        except Exception as e:
            logger.error(f"Error getting plan: {e}")
            return None
    
    def create_order(self, user_id: int, plan_id: int):
        try:
            with self.conn.cursor() as cur:
                cur.execute('''
                    INSERT INTO orders (user_id, plan_id) 
                    VALUES (%s, %s) 
                    RETURNING order_id
                ''', (user_id, plan_id))
                result = cur.fetchone()
                order_id = result['order_id'] if result else None
                self.conn.commit()
                return order_id
        except Exception as e:
            logger.error(f"Error creating order: {e}")
            return None
    
    def get_user_orders(self, user_id: int):
        try:
            with self.conn.cursor() as cur:
                cur.execute('''
                    SELECT o.*, p.name as plan_name, p.price 
                    FROM orders o 
                    JOIN plans p ON o.plan_id = p.plan_id 
                    WHERE o.user_id = %s 
                    ORDER BY o.created_at DESC
                ''', (user_id,))
                return cur.fetchall()
        except Exception as e:
            logger.error(f"Error getting user orders: {e}")
            return []
    
    def update_order_status(self, order_id: int, status: str, vpn_config: str = None):
        try:
            with self.conn.cursor() as cur:
                if vpn_config:
                    cur.execute('''
                        UPDATE orders SET status = %s, vpn_config = %s, updated_at = NOW()
                        WHERE order_id = %s
                    ''', (status, vpn_config, order_id))
                else:
                    cur.execute('''
                        UPDATE orders SET status = %s, updated_at = NOW()
                        WHERE order_id = %s
                    ''', (status, order_id))
                self.conn.commit()
        except Exception as e:
            logger.error(f"Error updating order status: {e}")
    
    def get_pending_orders(self):
        try:
            with self.conn.cursor() as cur:
                cur.execute('''
                    SELECT o.*, u.username, u.first_name, p.name as plan_name, p.price
                    FROM orders o
                    JOIN users u ON o.user_id = u.user_id
                    JOIN plans p ON o.plan_id = p.plan_id
                    WHERE o.status = 'pending'
                    ORDER BY o.created_at DESC
                ''')
                return cur.fetchall()
        except Exception as e:
            logger.error(f"Error getting pending orders: {e}")
            return []
    
    def add_log(self, user_id: int, action: str, details: str = ""):
        try:
            with self.conn.cursor() as cur:
                cur.execute('''
                    INSERT INTO logs (user_id, action, details)
                    VALUES (%s, %s, %s)
                ''', (user_id, action, details))
                self.conn.commit()
        except Exception as e:
            logger.error(f"Error adding log: {e}")

# ایجاد نمونه دیتابیس
db = Database()

def is_admin(user_id: int) -> bool:
    """بررسی اینکه کاربر ادمین هست یا نه"""
    return user_id == int(os.getenv('ADMIN_ID', 1606291654))

def get_admin_keyboard():
    """کیبورد مخصوص ادمین"""
    keyboard = [
        [InlineKeyboardButton("📊 مدیریت کاربران", callback_data="admin_users")],
        [InlineKeyboardButton("📦 مدیریت سفارشات", callback_data="admin_orders")],
        [InlineKeyboardButton("📋 مشاهده لاگ‌ها", callback_data="admin_logs")],
        [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_main_keyboard(is_admin_user: bool = False):
    """کیبورد اصلی کاربر"""
    keyboard = [
        [InlineKeyboardButton("🛒 خرید VPN", callback_data="buy_vpn")],
        [InlineKeyboardButton("📋 سفارشات من", callback_data="my_orders")],
        [InlineKeyboardButton("💰 کیف پول", callback_data="wallet")],
        [InlineKeyboardButton("ℹ️ راهنما", callback_data="help")]
    ]
    
    if is_admin_user:
        keyboard.append([InlineKeyboardButton("👨‍💼 پنل مدیریت", callback_data="admin_panel")])
    
    return InlineKeyboardMarkup(keyboard)

def get_plans_keyboard(plans):
    """کیبورد نمایش پلن‌ها"""
    keyboard = []
    for plan in plans:
        keyboard.append([
            InlineKeyboardButton(
                f"{plan['name']} - {plan['price']:,} تومان",
                callback_data=f"select_plan_{plan['plan_id']}"
            )
        ])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")])
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور شروع ربات"""
    try:
        user = update.effective_user
        user_id = user.id
        
        # ایجاد کاربر در دیتابیس
        db.create_user(user_id, user.username, user.first_name, user.last_name or "")
        db.add_log(user_id, "start", "کاربر ربات را شروع کرد")
        
        welcome_text = """
🤖 به ربات فروش VPN خوش آمدید!

🔒 با استفاده از این ربات می‌توانید:
• VPN پرسرعت خریداری کنید
• سفارشات خود را مدیریت کنید
• موجودی کیف پول خود را بررسی کنید

برای شروع از دکمه‌های زیر استفاده کنید:
"""
        
        keyboard = get_main_keyboard(is_admin(user_id))
        
        if update.callback_query:
            await update.callback_query.edit_message_text(welcome_text, reply_markup=keyboard)
        else:
            await update.message.reply_text(welcome_text, reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Error in start: {e}")

async def show_plans(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش پلن‌های موجود"""
    try:
        query = update.callback_query
        await query.answer()
        
        plans = db.get_plans()
        if not plans:
            await query.edit_message_text("⚠️ در حال حاضر پلنی برای فروش موجود نیست.")
            return
        
        plans_text = "🛒 پلن‌های موجود:\n\n"
        for plan in plans:
            plans_text += f"📦 {plan['name']}\n"
            plans_text += f"💰 قیمت: {plan['price']:,} تومان\n"
            plans_text += f"⏰ مدت: {plan['duration_days']} روز\n"
            plans_text += f"📝 {plan['description']}\n"
            plans_text += "─" * 30 + "\n"
        
        keyboard = get_plans_keyboard(plans)
        await query.edit_message_text(plans_text, reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Error in show_plans: {e}")

async def select_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """انتخاب پلن توسط کاربر"""
    try:
        query = update.callback_query
        await query.answer()
        
        plan_id = int(query.data.split('_')[-1])
        plan = db.get_plan(plan_id)
        user = db.get_user(query.from_user.id)
        
        if not plan:
            await query.edit_message_text("⚠️ پلن مورد نظر یافت نشد.")
            return
        
        # ایجاد سفارش
        order_id = db.create_order(user['user_id'], plan_id)
        if order_id:
            db.add_log(user['user_id'], "create_order", f"سفارش #{order_id} - پلن: {plan['name']}")
            
            order_text = f"""
📦 سفارش جدید ایجاد شد!

🆔 شماره سفارش: #{order_id}
📦 پلن: {plan['name']}
💰 مبلغ: {plan['price']:,} تومان
⏰ مدت: {plan['duration_days']} روز

✅ سفارش شما ثبت شد و در انتظار تایید ادمین است.

💳 برای پرداخت و دریافت کانفیگ با ادمین تماس بگیرید:
👤 @admin
"""
            
            # اطلاع به ادمین
            admin_id = int(os.getenv('ADMIN_ID', 1606291654))
            admin_text = f"""
🚨 سفارش جدید!

🆔 شماره سفارش: #{order_id}
👤 کاربر: {user['first_name']} (@{user.get('username', 'ندارد')})
🆔 User ID: {user['user_id']}
📦 پلن: {plan['name']}
💰 مبلغ: {plan['price']:,} تومان
⏰ مدت: {plan['duration_days']} روز
💳 موجودی کاربر: {user['balance']:,} تومان
"""
            
            try:
                await context.bot.send_message(admin_id, admin_text)
            except Exception as e:
                logger.error(f"Error sending admin notification: {e}")
        else:
            order_text = "❌ خطا در ایجاد سفارش. لطفا مجدد تلاش کنید."
        
        keyboard = [[InlineKeyboardButton("🔙 بازگشت به منو", callback_data="main_menu")]]
        await query.edit_message_text(order_text, reply_markup=InlineKeyboardMarkup(keyboard))
    except Exception as e:
        logger.error(f"Error in select_plan: {e}")

async def my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش سفارشات کاربر"""
    try:
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        orders = db.get_user_orders(user_id)
        
        if not orders:
            await query.edit_message_text("📭 شما هیچ سفارشی ندارید.")
            return
        
        orders_text = "📋 سفارشات شما:\n\n"
        for order in orders:
            status_emoji = {
                'pending': '⏳',
                'approved': '✅', 
                'rejected': '❌'
            }.get(order['status'], '📝')
            
            orders_text += f"{status_emoji} سفارش #{order['order_id']}\n"
            orders_text += f"📦 پلن: {order['plan_name']}\n"
            orders_text += f"💰 مبلغ: {order['price']:,} تومان\n"
            orders_text += f"📊 وضعیت: {order['status']}\n"
            created_at = order['created_at']
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            orders_text += f"📅 تاریخ: {created_at.strftime('%Y-%m-%d %H:%M')}\n"
            
            if order['vpn_config']:
                orders_text += f"🔑 کانفیگ: {order['vpn_config']}\n"
            
            orders_text += "─" * 30 + "\n"
        
        keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")]]
        await query.edit_message_text(orders_text, reply_markup=InlineKeyboardMarkup(keyboard))
    except Exception as e:
        logger.error(f"Error in my_orders: {e}")

async def wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش کیف پول کاربر"""
    try:
        query = update.callback_query
        await query.answer()
        
        user = db.get_user(query.from_user.id)
        
        wallet_text = f"""
💰 کیف پول شما:

💳 موجودی: {user['balance']:,} تومان

💵 برای شارژ کیف پول با ادمین تماس بگیرید:
👤 @admin
"""
        
        keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")]]
        await query.edit_message_text(wallet_text, reply_markup=InlineKeyboardMarkup(keyboard))
    except Exception as e:
        logger.error(f"Error in wallet: {e}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور راهنما"""
    try:
        query = update.callback_query
        await query.answer()
        
        help_text = """
ℹ️ راهنمای استفاده از ربات:

🛒 **خرید VPN:**
1. روی دکمه «خرید VPN» کلیک کنید
2. پلن مورد نظر را انتخاب کنید  
3. سفارش شما ثبت می‌شود
4. با ادمین برای پرداخت و دریافت کانفیگ تماس بگیرید

📋 **سفارشات من:**
• مشاهده تاریخچه سفارشات
• وضعیت هر سفارش
• کانفیگ VPN (در صورت تایید)

💰 **کیف پول:**
• مشاهده موجودی
• راهنمای شارژ

👤 **پشتیبانی:**
@admin
"""
        
        keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")]]
        await query.edit_message_text(help_text, reply_markup=InlineKeyboardMarkup(keyboard))
    except Exception as e:
        logger.error(f"Error in help_command: {e}")

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پنل مدیریت"""
    try:
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        if not is_admin(user_id):
            await query.edit_message_text("⛔ دسترسی denied.")
            return
        
        admin_text = """
👨‍💼 **پنل مدیریت**

لطفا یکی از گزینه‌های زیر را انتخاب کنید:
"""
        
        keyboard = get_admin_keyboard()
        await query.edit_message_text(admin_text, reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Error in admin_panel: {e}")

async def admin_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت سفارشات برای ادمین"""
    try:
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        if not is_admin(user_id):
            await query.edit_message_text("⛔ دسترسی denied.")
            return
        
        pending_orders = db.get_pending_orders()
        
        if not pending_orders:
            orders_text = "✅ هیچ سفارش در انتظاری وجود ندارد."
        else:
            orders_text = f"📦 سفارشات در انتظار: {len(pending_orders)}\n\n"
            for order in pending_orders[:10]:  # نمایش 10 سفارش اول
                orders_text += f"🆔 سفارش #{order['order_id']}\n"
                orders_text += f"👤 کاربر: {order['first_name']} (@{order.get('username', 'ندارد')})\n"
                orders_text += f"📦 پلن: {order['plan_name']}\n"
                orders_text += f"💰 مبلغ: {order['price']:,} تومان\n"
                orders_text += "─" * 30 + "\n"
        
        keyboard = [
            [InlineKeyboardButton("🔄 بروزرسانی", callback_data="admin_orders")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_panel")]
        ]
        
        await query.edit_message_text(orders_text, reply_markup=InlineKeyboardMarkup(keyboard))
    except Exception as e:
        logger.error(f"Error in admin_orders: {e}")

async def admin_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت کاربران برای ادمین"""
    try:
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        if not is_admin(user_id):
            await query.edit_message_text("⛔ دسترسی denied.")
            return
        
        # در این نسخه ساده، فقط یک پیام نمایش می‌دهیم
        users_text = "📊 مدیریت کاربران\n\nاین قابلیت در نسخه بعدی اضافه خواهد شد."
        
        keyboard = [
            [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_panel")]
        ]
        
        await query.edit_message_text(users_text, reply_markup=InlineKeyboardMarkup(keyboard))
    except Exception as e:
        logger.error(f"Error in admin_users: {e}")

async def admin_logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مشاهده لاگ‌ها برای ادمین"""
    try:
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        if not is_admin(user_id):
            await query.edit_message_text("⛔ دسترسی denied.")
            return
        
        logs_text = "📋 سیستم لاگ\n\nاین قابلیت در نسخه بعدی اضافه خواهد شد."
        
        keyboard = [
            [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_panel")]
        ]
        
        await query.edit_message_text(logs_text, reply_markup=InlineKeyboardMarkup(keyboard))
    except Exception as e:
        logger.error(f"Error in admin_logs: {e}")

def main():
    """تابع اصلی"""
    try:
        # اتصال به دیتابیس
        db.connect()
        
        # ایجاد اپلیکیشن
        BOT_TOKEN = os.getenv('BOT_TOKEN')
        if not BOT_TOKEN:
            logger.error("❌ BOT_TOKEN not found in environment variables")
            return
        
        application = Application.builder().token(BOT_TOKEN).build()
        
        # اضافه کردن هندلرها
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CallbackQueryHandler(start, pattern="^main_menu$"))
        application.add_handler(CallbackQueryHandler(show_plans, pattern="^buy_vpn$"))
        application.add_handler(CallbackQueryHandler(select_plan, pattern="^select_plan_"))
        application.add_handler(CallbackQueryHandler(my_orders, pattern="^my_orders$"))
        application.add_handler(CallbackQueryHandler(wallet, pattern="^wallet$"))
        application.add_handler(CallbackQueryHandler(help_command, pattern="^help$"))
        application.add_handler(CallbackQueryHandler(admin_panel, pattern="^admin_panel$"))
        application.add_handler(CallbackQueryHandler(admin_orders, pattern="^admin_orders$"))
        application.add_handler(CallbackQueryHandler(admin_users, pattern="^admin_users$"))
        application.add_handler(CallbackQueryHandler(admin_logs, pattern="^admin_logs$"))
        
        # شروع ربات
        logger.info("🤖 Bot is starting on Render with Docker...")
        application.run_polling()
        
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")

if __name__ == "__main__":
    main()

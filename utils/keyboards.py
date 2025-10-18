from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from app.config import config

def get_main_menu():
    """منوی اصلی"""
    keyboard = [
        [InlineKeyboardButton("🛒 خرید VPN", callback_data="buy_vpn")],
        [InlineKeyboardButton("📋 سفارشات من", callback_data="my_orders")],
        [InlineKeyboardButton("💰 کیف پول", callback_data="wallet")],
        [InlineKeyboardButton("ℹ️ راهنما", callback_data="help")],
        [InlineKeyboardButton("👨‍💼 پشتیبانی", callback_data="support")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_plans_keyboard():
    """کیبورد پلن‌ها"""
    keyboard = []
    for plan_id, plan_info in config.PLANS.items():
        keyboard.append([
            InlineKeyboardButton(
                f"{plan_info['name']} - {plan_info['price']:,} تومان", 
                callback_data=f"plan_{plan_id}"
            )
        ])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")])
    return InlineKeyboardMarkup(keyboard)

def get_admin_menu():
    """منوی ادمین"""
    keyboard = [
        [InlineKeyboardButton("👥 مدیریت کاربران", callback_data="admin_users")],
        [InlineKeyboardButton("📦 مدیریت سفارشات", callback_data="admin_orders")],
        [InlineKeyboardButton("👨‍💼 مدیریت ادمین‌ها", callback_data="admin_management")],
        [InlineKeyboardButton("💳 مدیریت پلن‌ها", callback_data="admin_plans")],
        [InlineKeyboardButton("📢 ارسال پیام گروهی", callback_data="admin_broadcast")],
        [InlineKeyboardButton("📊 آمار و گزارش‌ها", callback_data="admin_stats")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_order_actions_keyboard(order_id: int):
    """اقدامات روی سفارش برای ادمین"""
    keyboard = [
        [
            InlineKeyboardButton("✅ تایید", callback_data=f"approve_{order_id}"),
            InlineKeyboardButton("❌ رد", callback_data=f"reject_{order_id}")
        ],
        [
            InlineKeyboardButton("📁 آپلود فایل", callback_data=f"config_file_{order_id}"),
            InlineKeyboardButton("📝 ارسال متن", callback_data=f"config_text_{order_id}")
        ],
        [
            InlineKeyboardButton("🔗 ارسال لینک", callback_data=f"config_link_{order_id}"),
            InlineKeyboardButton("💬 یادداشت", callback_data=f"note_{order_id}")
        ],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_orders")]
    ]
    return InlineKeyboardMarkup(keyboard)

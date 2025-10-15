import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def is_admin(user_id: int) -> bool:
    """بررسی اینکه کاربر ادمین هست یا نه"""
    return user_id == int(os.getenv('ADMIN_ID'))

def get_admin_keyboard():
    """کیبورد مخصوص ادمین"""
    keyboard = [
        [InlineKeyboardButton("📊 مدیریت کاربران", callback_data="admin_users")],
        [InlineKeyboardButton("📦 مدیریت سفارشات", callback_data="admin_orders")],
        [InlineKeyboardButton("💳 مدیریت پلن‌ها", callback_data="admin_plans")],
        [InlineKeyboardButton("📝 ارسال پیام گروهی", callback_data="admin_broadcast")],
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

def format_user_info(user):
    """فرمت‌دهی اطلاعات کاربر"""
    return f"""
👤 اطلاعات کاربر:
🆔 ID: {user['user_id']}
👤 نام: {user['first_name']} {user.get('last_name', '')}
📛 username: @{user.get('username', 'ندارد')}
💳 موجودی: {user['balance']:,} تومان
👑 وضعیت: {'ادمین' if user['is_admin'] else 'کاربر عادی'}
📅 تاریخ عضویت: {user['created_at'].strftime('%Y-%m-%d %H:%M')}
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_main_keyboard(is_admin=False):
    """کیبورد اصلی کاربر"""
    keyboard = [
        [InlineKeyboardButton("🛒 خرید VPN", callback_data="buy_vpn")],
        [InlineKeyboardButton("📋 سفارشات من", callback_data="my_orders")],
        [InlineKeyboardButton("💰 کیف پول", callback_data="wallet")],
        [InlineKeyboardButton("🎫 پشتیبانی", callback_data="support")],
        [InlineKeyboardButton("ℹ️ راهنما", callback_data="help")]
    ]
    
    if is_admin:
        keyboard.append([InlineKeyboardButton("👨‍💼 پنل مدیریت", callback_data="admin_panel")])
    
    return InlineKeyboardMarkup(keyboard)

def get_admin_keyboard():
    """کیبورد مخصوص ادمین"""
    keyboard = [
        [InlineKeyboardButton("📊 مدیریت کاربران", callback_data="admin_users")],
        [InlineKeyboardButton("📦 مدیریت سفارشات", callback_data="admin_orders")],
        [InlineKeyboardButton("💳 مدیریت پلن‌ها", callback_data="admin_plans")],
        [InlineKeyboardButton("📝 ارسال پیام گروهی", callback_data="admin_broadcast")],
        [InlineKeyboardButton("🎫 تیکت‌های پشتیبانی", callback_data="admin_tickets")],
        [InlineKeyboardButton("📋 مشاهده لاگ‌ها", callback_data="admin_logs")],
        [InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="main_menu")]
    ]
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

def get_support_keyboard():
    """کیبورد پشتیبانی"""
    keyboard = [
        [InlineKeyboardButton("🎫 ایجاد تیکت جدید", callback_data="create_ticket")],
        [InlineKeyboardButton("📋 تیکت‌های من", callback_data="my_tickets")],
        [InlineKeyboardButton("📞 تماس با ادمین", url="https://t.me/username")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_order_actions_keyboard(order_id):
    """کیبورد اقدامات برای سفارش"""
    keyboard = [
        [
            InlineKeyboardButton("✅ تایید", callback_data=f"approve_order_{order_id}"),
            InlineKeyboardButton("❌ رد", callback_data=f"reject_order_{order_id}")
        ],
        [InlineKeyboardButton("📋 مدیریت سفارشات", callback_data="admin_orders")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_keyboard(target="main_menu"):
    """کیبورد بازگشت"""
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data=target)]])

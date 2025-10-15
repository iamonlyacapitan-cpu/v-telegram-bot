import datetime

# ---------- زمان و تاریخ ----------
def now():
    """زمان فعلی را به فرمت datetime برمی‌گرداند"""
    return datetime.datetime.now()

def format_datetime(dt: datetime.datetime):
    """تاریخ را به رشته فارسی-friendly تبدیل می‌کند"""
    return dt.strftime("%Y-%m-%d %H:%M:%S")

# ---------- منوها و InlineKeyboard ----------
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def build_inline_keyboard(buttons):
    """
    دیکشنری یا لیست دکمه‌ها را به InlineKeyboardMarkup تبدیل می‌کند
    Example: [[("نام دکمه", "callback_data")], [...]]
    """
    keyboard = [
        [InlineKeyboardButton(text, callback_data=data) for text, data in row]
        for row in buttons
    ]
    return InlineKeyboardMarkup(keyboard)

# ---------- بررسی عدد ----------
def is_positive_int(value):
    """بررسی می‌کند که مقدار یک عدد مثبت صحیح است یا خیر"""
    try:
        v = int(value)
        return v > 0
    except:
        return False

# ---------- پیام‌ها ----------
def format_wallet(amount):
    """موجودی کیف‌پول را به رشته قابل خواندن تبدیل می‌کند"""
    return f"{amount:,} تومان"

def format_plan(plan):
    """پلن را به متن قابل نمایش تبدیل می‌کند"""
    return f"🔹 {plan['name']} - {plan['price']:,} تومان\n{plan['description']}"

def format_order(order):
    """سفارش را به متن قابل نمایش تبدیل می‌کند"""
    return f"سفارش #{order['id']} - وضعیت: {order['status']}"

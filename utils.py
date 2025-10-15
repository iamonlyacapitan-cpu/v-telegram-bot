import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def now():
    return datetime.datetime.now()

def format_datetime(dt: datetime.datetime):
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def build_inline_keyboard(buttons):
    """
    buttons = [[("نام دکمه", "callback_data")], [...]]
    """
    keyboard = [
        [InlineKeyboardButton(text, callback_data=data) for text, data in row]
        for row in buttons
    ]
    return InlineKeyboardMarkup(keyboard)

def is_positive_int(value):
    try:
        v = int(value)
        return v > 0
    except:
        return False

def format_wallet(amount):
    return f"{amount:,} تومان"

def format_plan(plan):
    return f"🔹 {plan['name']} - {plan['price']:,} تومان\n{plan['description']}"

def format_order(order):
    return f"سفارش #{order['id']} - وضعیت: {order['status']}"

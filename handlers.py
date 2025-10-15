from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from db import register_user, is_admin, add_log

# Handler دستور /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pool = context.bot_data['db_pool']  # استفاده از pool مشترک
    tg = update.effective_user

    # ثبت کاربر و لاگ
    await register_user(pool, tg.id)
    await add_log(pool, tg.id, "start")

    # کیبورد اصلی
    keyboard = [
        [InlineKeyboardButton("💰 پلن‌ها", callback_data="show_plans")],
        [InlineKeyboardButton("🧾 سفارش‌های من", callback_data="my_orders")],
        [InlineKeyboardButton("💳 کیف پول", callback_data="wallet")],
    ]

    # اگر ادمین بود، گزینه‌ی پنل مدیریت اضافه شود
    if await is_admin(pool, tg.id):
        keyboard.append([InlineKeyboardButton("⚙️ پنل مدیریت", callback_data="admin_panel")])

    await update.message.reply_text(
        "سلام! خوش آمدی به پینگ‌من ⚡",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Callback handler ها
async def show_plans(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.reply_text("لیست پلن‌ها در اینجا نمایش داده می‌شود.")

async def my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.reply_text("سفارش‌های شما در اینجا نمایش داده می‌شود.")

async def wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.reply_text("موجودی کیف پول شما نمایش داده می‌شود.")

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.reply_text("پنل مدیریت ⚙️")

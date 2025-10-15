from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from db import register_user, add_log, is_admin

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pool = context.bot_data['db_pool']
    tg = update.effective_user
    await register_user(pool, tg.id)
    await add_log(pool, tg.id, "start")
    keyboard = [
        [InlineKeyboardButton("💰 پلن‌ها", callback_data="show_plans")],
        [InlineKeyboardButton("🧾 سفارش‌های من", callback_data="my_orders")],
        [InlineKeyboardButton("💳 کیف پول", callback_data="wallet")],
    ]
    if await is_admin(pool, tg.id):
        keyboard.append([InlineKeyboardButton("⚙️ پنل مدیریت", callback_data="admin_panel")])
    await update.message.reply_text("سلام! خوش آمدی به پینگ‌من ⚡", reply_markup=InlineKeyboardMarkup(keyboard))

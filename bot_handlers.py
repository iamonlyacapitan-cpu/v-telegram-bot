from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from db import register_user, add_log, is_admin, get_wallet, update_wallet

# ---------- Handlers ----------
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

async def wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pool = context.bot_data['db_pool']
    tg = update.effective_user
    amount = await get_wallet(pool, tg.id)
    await update.message.reply_text(f"💳 موجودی کیف‌پول شما: {amount} تومان")

# ⚡ سایر callbackها: show_plans, my_orders, admin_panel, add_plan, edit_plan, delete_plan
# approve_order, reject_order, add_admin, remove_admin
# ثبت رسید و ارسال کانفیگ دستی
# تمام اینها در همین فایل قابل گسترش هستند

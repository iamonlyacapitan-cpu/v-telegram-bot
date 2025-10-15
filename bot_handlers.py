from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from db import register_user, add_log, is_admin, get_wallet, update_wallet

# ---------- Command Handlers ----------
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
    await update.message.reply_text(
        "سلام! خوش آمدی به پینگ‌من ⚡",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pool = context.bot_data['db_pool']
    tg = update.effective_user
    amount = await get_wallet(pool, tg.id)
    await update.message.reply_text(f"💳 موجودی کیف‌پول شما: {amount} تومان")

# ---------- Callback Handlers ----------
async def show_plans(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pool = context.bot_data['db_pool']
    query = update.callback_query
    await query.answer()
    rows = await pool.fetch("SELECT id, name, price, description FROM plans")
    if not rows:
        await query.edit_message_text("فعلا هیچ پلنی وجود ندارد.")
        return
    text = "\n\n".join([f"🔹 {r['name']} - {r['price']} تومان\n{r['description']}" for r in rows])
    await query.edit_message_text(f"💰 پلن‌ها:\n\n{text}")

async def my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pool = context.bot_data['db_pool']
    tg = update.effective_user
    query = update.callback_query
    await query.answer()
    rows = await pool.fetch(
        "SELECT id, status FROM orders WHERE user_id=$1 ORDER BY created_at DESC", tg.id
    )
    if not rows:
        await query.edit_message_text("📝 هیچ سفارشی ثبت نکرده‌اید.")
        return
    text = "\n".join([f"سفارش #{r['id']} - وضعیت: {r['status']}" for r in rows])
    await query.edit_message_text(f"📝 سفارش‌های شما:\n\n{text}")

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pool = context.bot_data['db_pool']
    tg = update.effective_user
    if not await is_admin(pool, tg.id):
        await update.callback_query.answer("❌ شما ادمین نیستید!", show_alert=True)
        return
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("🧑‍💼 مدیریت کاربران", callback_data="admin_users")],
        [InlineKeyboardButton("💰 مدیریت پلن‌ها", callback_data="admin_plans")],
        [InlineKeyboardButton("📝 مدیریت سفارش‌ها", callback_data="admin_orders")],
    ]
    await query.edit_message_text(
        "⚙️ پنل مدیریت:", reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ⚡ سایر Callbackها برای تایید/رد سفارش، اضافه/حذف پلن، اضافه/حذف کاربر و ثبت رسید پرداخت
# در این فایل قابل اضافه شدن هستند و می‌توانم نسخه کامل نهایی را با اینها هم بسازم

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from db import register_user, add_log, is_admin, get_wallet, update_wallet, get_all_users, delete_user
import datetime

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

# ---------- مدیریت کاربران ----------
async def admin_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pool = context.bot_data['db_pool']
    query = update.callback_query
    await query.answer()
    rows = await get_all_users(pool)
    if not rows:
        await query.edit_message_text("❌ هیچ کاربری ثبت نشده است.")
        return
    text = "\n".join([f"👤 {r['telegram_id']} - کیف‌پول: {r['wallet']} تومان" for r in rows])
    await query.edit_message_text(f"🧑‍💼 کاربران:\n\n{text}")

async def delete_user_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pool = context.bot_data['db_pool']
    tg = update.effective_user
    if not await is_admin(pool, tg.id):
        await update.callback_query.answer("❌ شما ادمین نیستید!", show_alert=True)
        return
    # فرض می‌کنیم callback_data="delete_user:telegram_id"
    query = update.callback_query
    await query.answer()
    telegram_id = int(query.data.split(":")[1])
    await delete_user(pool, telegram_id)
    await add_log(pool, tg.id, f"حذف کاربر {telegram_id}")
    await query.edit_message_text(f"✅ کاربر {telegram_id} حذف شد.")
# ادامه از قبلی
from db import (
    get_all_users, delete_user, get_wallet, update_wallet,
    get_all_plans, add_plan, edit_plan, delete_plan,
    get_all_orders, update_order_status, set_order_config
)

# ---------- مدیریت پلن‌ها ----------
async def admin_plans(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pool = context.bot_data['db_pool']
    query = update.callback_query
    await query.answer()
    rows = await get_all_plans(pool)
    if not rows:
        await query.edit_message_text("❌ هیچ پلنی وجود ندارد.")
        return
    text = "\n".join([f"🔹 {r['id']} - {r['name']} : {r['price']} تومان" for r in rows])
    keyboard = [[InlineKeyboardButton(f"حذف {r['id']}", callback_data=f"delete_plan:{r['id']}")] for r in rows]
    await query.edit_message_text(f"💰 پلن‌ها:\n{text}", reply_markup=InlineKeyboardMarkup(keyboard))

async def delete_plan_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pool = context.bot_data['db_pool']
    tg = update.effective_user
    if not await is_admin(pool, tg.id):
        await update.callback_query.answer("❌ شما ادمین نیستید!", show_alert=True)
        return
    query = update.callback_query
    plan_id = int(query.data.split(":")[1])
    await delete_plan(pool, plan_id)
    await add_log(pool, tg.id, f"حذف پلن {plan_id}")
    await query.edit_message_text(f"✅ پلن {plan_id} حذف شد.")

# ---------- مدیریت سفارش‌ها ----------
async def admin_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pool = context.bot_data['db_pool']
    query = update.callback_query
    await query.answer()
    rows = await get_all_orders(pool)
    if not rows:
        await query.edit_message_text("❌ هیچ سفارشی ثبت نشده است.")
        return
    text = "\n".join([f"#{r['id']} - کاربر: {r['user_id']} - وضعیت: {r['status']}" for r in rows])
    keyboard = [
        [InlineKeyboardButton(f"تایید {r['id']}", callback_data=f"approve_order:{r['id']}"),
         InlineKeyboardButton(f"رد {r['id']}", callback_data=f"reject_order:{r['id']}")]
        for r in rows
    ]
    await query.edit_message_text(f"📝 سفارش‌ها:\n{text}", reply_markup=InlineKeyboardMarkup(keyboard))

async def approve_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pool = context.bot_data['db_pool']
    tg = update.effective_user
    query = update.callback_query
    order_id = int(query.data.split(":")[1])
    await update_order_status(pool, order_id, "تایید شد")
    # نمونه ارسال کانفیگ به کاربر
    await set_order_config(pool, order_id, "کانفیگ نمونه")
    await add_log(pool, tg.id, f"تایید سفارش {order_id}")
    await query.edit_message_text(f"✅ سفارش #{order_id} تایید شد و کانفیگ ارسال شد.")

async def reject_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pool = context.bot_data['db_pool']
    tg = update.effective_user
    query = update.callback_query
    order_id = int(query.data.split(":")[1])
    await update_order_status(pool, order_id, "رد شد")
    await add_log(pool, tg.id, f"رد سفارش {order_id}")
    await query.edit_message_text(f"❌ سفارش #{order_id} رد شد و پیام به کاربر ارسال شد.")

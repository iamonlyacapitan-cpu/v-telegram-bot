from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from db import register_user, add_log, is_admin, get_all_plans, delete_plan, get_all_orders, update_order_status, set_order_config
from utils import build_inline_keyboard

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

# Admin: Plans
async def admin_plans(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pool = context.bot_data['db_pool']
    query = update.callback_query
    await query.answer()
    rows = await get_all_plans(pool)
    if not rows:
        await query.edit_message_text("❌ هیچ پلنی وجود ندارد.")
        return
    text = "\n".join([f"{r['id']} - {r['name']} : {r['price']}" for r in rows])
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

# Admin: Orders
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

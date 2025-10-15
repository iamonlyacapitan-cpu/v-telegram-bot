from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, MessageHandler, filters
from database import db
from utils.helpers import get_main_keyboard, get_plans_keyboard, is_admin, format_user_info
import logging

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور شروع ربات"""
    user = update.effective_user
    user_id = user.id
    
    # ایجاد کاربر در دیتابیس
    await db.create_user(user_id, user.username, user.first_name, user.last_name or "")
    await db.add_log(user_id, "start", "کاربر ربات را شروع کرد")
    
    welcome_text = """
🤖 به ربات فروش VPN خوش آمدید!

🔒 با استفاده از این ربات می‌توانید:
• VPN پرسرعت خریداری کنید
• سفارشات خود را مدیریت کنید
• موجودی کیف پول خود را بررسی کنید

برای شروع از دکمه‌های زیر استفاده کنید:
"""
    
    keyboard = get_main_keyboard(is_admin(user_id))
    
    if update.callback_query:
        await update.callback_query.edit_message_text(welcome_text, reply_markup=keyboard)
    else:
        await update.message.reply_text(welcome_text, reply_markup=keyboard)

async def show_plans(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش پلن‌های موجود"""
    query = update.callback_query
    await query.answer()
    
    plans = await db.get_plans()
    if not plans:
        await query.edit_message_text("⚠️ در حال حاضر پلنی برای فروش موجود نیست.")
        return
    
    plans_text = "🛒 پلن‌های موجود:\n\n"
    for plan in plans:
        plans_text += f"📦 {plan['name']}\n"
        plans_text += f"💰 قیمت: {plan['price']:,} تومان\n"
        plans_text += f"⏰ مدت: {plan['duration_days']} روز\n"
        plans_text += f"📝 {plan['description']}\n"
        plans_text += "─" * 30 + "\n"
    
    keyboard = get_plans_keyboard(plans)
    await query.edit_message_text(plans_text, reply_markup=keyboard)

async def select_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """انتخاب پلن توسط کاربر"""
    query = update.callback_query
    await query.answer()
    
    plan_id = int(query.data.split('_')[-1])
    plan = await db.get_plan(plan_id)
    user = await db.get_user(query.from_user.id)
    
    if not plan:
        await query.edit_message_text("⚠️ پلن مورد نظر یافت نشد.")
        return
    
    # ایجاد سفارش
    order_id = await db.create_order(user['user_id'], plan_id)
    await db.add_log(user['user_id'], "create_order", f"سفارش جدید - پلن: {plan['name']}")
    
    order_text = f"""
📦 سفارش جدید ایجاد شد:

🆔 شماره سفارش: {order_id}
📦 پلن: {plan['name']}
💰 مبلغ: {plan['price']:,} تومان
⏰ مدت: {plan['duration_days']} روز

"""
    
    if user['balance'] >= plan['price']:
        # اگر موجودی کافی دارد
        order_text += "✅ موجودی شما کافی است. لطفا منتظر تایید ادمین باشید."
        keyboard = [[InlineKeyboardButton("🔙 بازگشت به منو", callback_data="main_menu")]]
    else:
        # اگر موجودی کافی ندارد
        order_text += f"""
❌ موجودی شما کافی نیست.
💳 موجودی فعلی: {user['balance']:,} تومان
💰 مبلغ مورد نیاز: {plan['price']:,} تومان

لطفا مبلغ {plan['price']:,} تومان به شماره کارت زیر واریز کنید و رسید را ارسال نمایید:

🏦 بانک: ملت
💳 شماره کارت: 6104 3378 1234 5678
👤 به نام: جان دون

سپس رسید پرداخت را در این چت آپلود کنید.
"""
        keyboard = [[InlineKeyboardButton("🔙 بازگشت به منو", callback_data="main_menu")]]
    
    # اطلاع به ادمین
    admin_id = int(context.bot_data['ADMIN_ID'])
    admin_text = f"""
🚨 سفارش جدید!

🆔 شماره سفارش: {order_id}
👤 کاربر: {user['first_name']} (@{user.get('username', 'ندارد')})
📦 پلن: {plan['name']}
💰 مبلغ: {plan['price']:,} تومان
💳 موجودی کاربر: {user['balance']:,} تومان
"""
    
    admin_keyboard = [
        [InlineKeyboardButton("✅ تایید سفارش", callback_data=f"approve_order_{order_id}")],
        [InlineKeyboardButton("❌ رد سفارش", callback_data=f"reject_order_{order_id}")],
        [InlineKeyboardButton("📋 مدیریت سفارشات", callback_data="admin_orders")]
    ]
    
    try:
        await context.bot.send_message(
            admin_id, 
            admin_text, 
            reply_markup=InlineKeyboardMarkup(admin_keyboard)
        )
    except Exception as e:
        logger.error(f"خطا در ارسال پیام به ادمین: {e}")
    
    await query.edit_message_text(order_text, reply_markup=InlineKeyboardMarkup(keyboard))

async def my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش سفارشات کاربر"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    orders = await db.get_user_orders(user_id)
    
    if not orders:
        await query.edit_message_text("📭 شما هیچ سفارشی ندارید.")
        return
    
    orders_text = "📋 سفارشات شما:\n\n"
    for order in orders:
        status_emoji = {
            'pending': '⏳',
            'approved': '✅',
            'rejected': '❌'
        }.get(order['status'], '📝')
        
        orders_text += f"{status_emoji} سفارش #{order['order_id']}\n"
        orders_text += f"📦 پلن: {order['plan_name']}\n"
        orders_text += f"💰 مبلغ: {order['price']:,} تومان\n"
        orders_text += f"📊 وضعیت: {order['status']}\n"
        orders_text += f"📅 تاریخ: {order['created_at'].strftime('%Y-%m-%d %H:%M')}\n"
        
        if order['vpn_config']:
            orders_text += f"🔑 کانفیگ: {order['vpn_config']}\n"
        
        orders_text += "─" * 30 + "\n"
    
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")]]
    await query.edit_message_text(orders_text, reply_markup=InlineKeyboardMarkup(keyboard))

async def wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش کیف پول کاربر"""
    query = update.callback_query
    await query.answer()
    
    user = await db.get_user(query.from_user.id)
    
    wallet_text = f"""
💰 کیف پول شما:

💳 موجودی: {user['balance']:,} تومان

برای شارژ کیف پول با پشتیبانی تماس بگیرید.
"""
    
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")]]
    await query.edit_message_text(wallet_text, reply_markup=InlineKeyboardMarkup(keyboard))

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور راهنما"""
    query = update.callback_query
    await query.answer()
    
    help_text = """
ℹ️ راهنمای استفاده از ربات:

🛒 خرید VPN:
1. روی دکمه «خرید VPN» کلیک کنید
2. پلن مورد نظر را انتخاب کنید
3. اگر موجودی کافی دارید، سفارش ثبت می‌شود
4. اگر موجودی کافی ندارید، رسید پرداخت را ارسال کنید

📋 سفارشات من:
• مشاهده تاریخچه سفارشات
• وضعیت هر سفارش
• کانفیگ VPN (در صورت تایید)

💰 کیف پول:
• مشاهده موجودی
• راهنمای شارژ

📞 پشتیبانی:
برای مشکلات فنی با ادمین تماس بگیرید.
"""
    
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")]]
    await query.edit_message_text(help_text, reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پردازش رسید پرداخت کاربر"""
    user_id = update.message.from_user.id
    user = await db.get_user(user_id)
    
    if update.message.photo:
        # اگر کاربر عکس ارسال کرده
        file_id = update.message.photo[-1].file_id
        receipt_text = "عکس رسید پرداخت"
    elif update.message.document:
        # اگر کاربر فایل ارسال کرده
        file_id = update.message.document.file_id
        receipt_text = "فایل رسید پرداخت"
    else:
        await update.message.reply_text("⚠️ لطفا عکس یا فایل رسید پرداخت را ارسال کنید.")
        return
    
    # ذخیره اطلاعات رسید (در اینجا فقط file_id ذخیره می‌شود)
    # در نسخه واقعی باید فایل دانلود و ذخیره شود
    
    # اطلاع به ادمین
    admin_id = int(context.bot_data['ADMIN_ID'])
    admin_text = f"""
📨 رسید پرداخت جدید از کاربر:

👤 کاربر: {user['first_name']} (@{user.get('username', 'ندارد')})
🆔 ID: {user_id}
📎 نوع رسید: {receipt_text}

لطفا رسید را بررسی و سفارش را تایید یا رد کنید.
"""
    
    # ارسال رسید به ادمین
    try:
        if update.message.photo:
            await context.bot.send_photo(
                admin_id, 
                file_id, 
                caption=admin_text
            )
        else:
            await context.bot.send_document(
                admin_id, 
                file_id, 
                caption=admin_text
            )
    except Exception as e:
        logger.error(f"خطا در ارسال رسید به ادمین: {e}")
        await update.message.reply_text("⚠️ خطا در ارسال رسید. لطفا بعدا تلاش کنید.")
        return
    
    await update.message.reply_text(
        "✅ رسید پرداخت شما دریافت شد و به ادمین ارسال گردید. "
        "لطفا منتظر بررسی و تایید باشید."
    )
    
    await db.add_log(user_id, "upload_receipt", receipt_text)

# ثبت هندلرها
user_handlers = [
    CallbackQueryHandler(start, pattern="^main_menu$"),
    CallbackQueryHandler(show_plans, pattern="^buy_vpn$"),
    CallbackQueryHandler(select_plan, pattern="^select_plan_"),
    CallbackQueryHandler(my_orders, pattern="^my_orders$"),
    CallbackQueryHandler(wallet, pattern="^wallet$"),
    CallbackQueryHandler(help_command, pattern="^help$"),
    MessageHandler(filters.PHOTO | filters.Document.ALL, handle_receipt)
]

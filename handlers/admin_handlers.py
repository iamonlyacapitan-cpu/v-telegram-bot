from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, MessageHandler, filters
from database import db
from utils.helpers import get_admin_keyboard, get_main_keyboard, format_user_info
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# حالت‌های مختلف برای پنل ادمین
class AdminStates:
    BROADCAST_MESSAGE = "broadcast_message"
    BROADCAST_PHOTO = "broadcast_photo"
    SEND_MESSAGE_TO_USER = "send_message_to_user"
    ADD_PLAN = "add_plan"

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش پنل مدیریت"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    if not await is_admin(user_id):
        await query.edit_message_text("⛔ دسترسی denied.")
        return
    
    admin_text = """
👨‍💼 **پنل مدیریت**

لطفا یکی از گزینه‌های زیر را انتخاب کنید:
"""
    
    keyboard = get_admin_keyboard()
    await query.edit_message_text(admin_text, reply_markup=keyboard)

async def admin_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت کاربران"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    if not await is_admin(user_id):
        await query.edit_message_text("⛔ دسترسی denied.")
        return
    
    users = await db.get_all_users()
    
    users_text = f"👥 مدیریت کاربران - تعداد: {len(users)}\n\n"
    
    # نمایش 10 کاربر اول
    for i, user in enumerate(users[:10], 1):
        users_text += f"{i}. {user['first_name']} - @{user.get('username', 'ندارد')}\n"
        users_text += f"   🆔 ID: {user['user_id']} | 📦 سفارشات: {user['order_count']}\n"
        users_text += f"   💰 موجودی: {user['balance']:,} تومان\n"
        users_text += "─" * 30 + "\n"
    
    if len(users) > 10:
        users_text += f"\n📊 و {len(users) - 10} کاربر دیگر..."
    
    keyboard = [
        [InlineKeyboardButton("🔍 جستجوی کاربر", callback_data="search_user")],
        [InlineKeyboardButton("📊 آمار کلی", callback_data="user_stats")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_panel")]
    ]
    
    await query.edit_message_text(users_text, reply_markup=InlineKeyboardMarkup(keyboard))

async def admin_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت سفارشات"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    if not await is_admin(user_id):
        await query.edit_message_text("⛔ دسترسی denied.")
        return
    
    pending_orders = await db.get_pending_orders()
    
    orders_text = f"📦 مدیریت سفارشات - در انتظار: {len(pending_orders)}\n\n"
    
    if not pending_orders:
        orders_text += "✅ هیچ سفارش در انتظاری وجود ندارد."
    else:
        for order in pending_orders[:5]:
            orders_text += f"🆔 سفارش #{order['order_id']}\n"
            orders_text += f"👤 کاربر: {order['first_name']} (@{order.get('username', 'ندارد')})\n"
            orders_text += f"📦 پلن: {order['plan_name']}\n"
            orders_text += f"💰 مبلغ: {order['price']:,} تومان\n"
            orders_text += f"📅 تاریخ: {order['created_at'].strftime('%Y-%m-%d %H:%M')}\n"
            
            keyboard_line = []
            if len(pending_orders) <= 5:
                keyboard_line.extend([
                    InlineKeyboardButton(f"✅ #{order['order_id']}", callback_data=f"approve_order_{order['order_id']}"),
                    InlineKeyboardButton(f"❌ #{order['order_id']}", callback_data=f"reject_order_{order['order_id']}")
                ])
            
            orders_text += "─" * 30 + "\n"
    
    keyboard = [
        [InlineKeyboardButton("📋 همه سفارشات", callback_data="all_orders")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_panel")]
    ]
    
    # اضافه کردن دکمه‌های سریع برای سفارشات
    if pending_orders:
        quick_buttons = []
        for order in pending_orders[:3]:
            quick_buttons.append(
                InlineKeyboardButton(f"⚡ #{order['order_id']}", callback_data=f"quick_view_{order['order_id']}")
            )
        if quick_buttons:
            keyboard.insert(0, quick_buttons)
    
    await query.edit_message_text(orders_text, reply_markup=InlineKeyboardMarkup(keyboard))

async def approve_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تایید سفارش توسط ادمین"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    if not await is_admin(user_id):
        await query.edit_message_text("⛔ دسترسی denied.")
        return
    
    order_id = int(query.data.split('_')[-1])
    
    # درخواست کانفیگ VPN از ادمین
    context.user_data['awaiting_vpn_config'] = order_id
    await query.edit_message_text(
        f"✅ سفارش #{order_id} تایید شد.\n\n"
        "لطفا کانفیگ VPN را وارد کنید:"
    )

async def reject_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """رد سفارش توسط ادمین"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    if not await is_admin(user_id):
        await query.edit_message_text("⛔ دسترسی denied.")
        return
    
    order_id = int(query.data.split('_')[-1])
    
    # درخواست دلیل رد از ادمین
    context.user_data['rejecting_order'] = order_id
    await query.edit_message_text(
        f"❌ سفارش #{order_id} رد شد.\n\n"
        "لطفا دلیل رد را وارد کنید:"
    )

async def handle_vpn_config(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پردازش کانفیگ VPN از ادمین"""
    user_id = update.message.from_user.id
    if not await is_admin(user_id):
        await update.message.reply_text("⛔ دسترسی denied.")
        return
    
    if 'awaiting_vpn_config' not in context.user_data:
        await update.message.reply_text("⚠️ دستور نامعتبر.")
        return
    
    order_id = context.user_data['awaiting_vpn_config']
    vpn_config = update.message.text
    
    # آپدیت وضعیت سفارش
    await db.update_order_status(order_id, 'approved', vpn_config)
    
    # دریافت اطلاعات سفارش برای اطلاع به کاربر
    orders = await db.get_pending_orders()
    order_info = None
    for order in orders:
        if order['order_id'] == order_id:
            order_info = order
            break
    
    if order_info:
        # اطلاع به کاربر
        user_notification = f"""
✅ سفارش شما تایید شد!

🆔 شماره سفارش: #{order_id}
📦 پلن: {order_info['plan_name']}
🔑 کانفیگ VPN: 
{vpn_config}

📝 راهنمای استفاده:
1. اپلیکیشن OpenVPN را نصب کنید
2. کانفیگ بالا را import کنید
3. اتصال را برقرار کنید

برای سوالات با پشتیبانی تماس بگیرید.
"""
        try:
            await context.bot.send_message(order_info['user_id'], user_notification)
        except Exception as e:
            logger.error(f"خطا در ارسال پیام به کاربر: {e}")
    
    await db.add_log(user_id, "approve_order", f"سفارش #{order_id} تایید شد")
    
    await update.message.reply_text(
        f"✅ کانفیگ برای سفارش #{order_id} ثبت شد و به کاربر اطلاع داده شد.",
        reply_markup=get_admin_keyboard()
    )
    
    # پاک کردن حالت
    del context.user_data['awaiting_vpn_config']

async def handle_reject_reason(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پردازش دلیل رد سفارش از ادمین"""
    user_id = update.message.from_user.id
    if not await is_admin(user_id):
        await update.message.reply_text("⛔ دسترسی denied.")
        return
    
    if 'rejecting_order' not in context.user_data:
        await update.message.reply_text("⚠️ دستور نامعتبر.")
        return
    
    order_id = context.user_data['rejecting_order']
    reject_reason = update.message.text
    
    # آپدیت وضعیت سفارش
    await db.update_order_status(order_id, 'rejected', admin_note=reject_reason)
    
    # دریافت اطلاعات سفارش برای اطلاع به کاربر
    orders = await db.get_pending_orders()
    order_info = None
    for order in orders:
        if order['order_id'] == order_id:
            order_info = order
            break
    
    if order_info:
        # اطلاع به کاربر
        user_notification = f"""
❌ سفارش شما رد شد.

🆔 شماره سفارش: #{order_id}
📦 پلن: {order_info['plan_name']}
📝 دلیل: {reject_reason}

در صورت نیاز به اطلاعات بیشتر با پشتیبانی تماس بگیرید.
"""
        try:
            await context.bot.send_message(order_info['user_id'], user_notification)
        except Exception as e:
            logger.error(f"خطا در ارسال پیام به کاربر: {e}")
    
    await db.add_log(user_id, "reject_order", f"سفارش #{order_id} رد شد")
    
    await update.message.reply_text(
        f"❌ سفارش #{order_id} رد شد و به کاربر اطلاع داده شد.",
        reply_markup=get_admin_keyboard()
    )
    
    # پاک کردن حالت
    del context.user_data['rejecting_order']

async def admin_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ارسال پیام گروهی"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    if not await is_admin(user_id):
        await query.edit_message_text("⛔ دسترسی denied.")
        return
    
    broadcast_text = """
📢 **ارسال پیام گروهی**

لطفا نوع پیام را انتخاب کنید:

• 📝 ارسال متن
• 🖼️ ارسال عکس با کپشن
• 👤 ارسال به کاربر خاص
"""
    
    keyboard = [
        [InlineKeyboardButton("📝 ارسال متن", callback_data="broadcast_text")],
        [InlineKeyboardButton("🖼️ ارسال عکس", callback_data="broadcast_photo")],
        [InlineKeyboardButton("👤 ارسال به کاربر خاص", callback_data="broadcast_user")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_panel")]
    ]
    
    await query.edit_message_text(broadcast_text, reply_markup=InlineKeyboardMarkup(keyboard))

async def start_broadcast_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع ارسال پیام متنی گروهی"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    if not await is_admin(user_id):
        await query.edit_message_text("⛔ دسترسی denied.")
        return
    
    context.user_data['broadcast_type'] = 'text'
    await query.edit_message_text(
        "📝 لطفا متن پیام گروهی را وارد کنید:\n\n"
        "⚠️ توجه: این پیام به همه کاربران ارسال خواهد شد."
    )

async def start_broadcast_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع ارسال عکس گروهی"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    if not await is_admin(user_id):
        await query.edit_message_text("⛔ دسترسی denied.")
        return
    
    context.user_data['broadcast_type'] = 'photo'
    await query.edit_message_text(
        "🖼️ لطفا عکس مورد نظر را به همراه کپشن ارسال کنید:\n\n"
        "⚠️ توجه: این پیام به همه کاربران ارسال خواهد شد."
    )

async def handle_broadcast_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پردازش پیام متنی گروهی"""
    user_id = update.message.from_user.id
    if not await is_admin(user_id):
        await update.message.reply_text("⛔ دسترسی denied.")
        return
    
    if context.user_data.get('broadcast_type') != 'text':
        await update.message.reply_text("⚠️ دستور نامعتبر.")
        return
    
    message_text = update.message.text
    users = await db.get_all_users()
    
    success_count = 0
    fail_count = 0
    
    # ارسال به همه کاربران
    for user in users:
        try:
            await context.bot.send_message(user['user_id'], message_text)
            success_count += 1
        except Exception as e:
            fail_count += 1
            logger.error(f"خطا در ارسال به کاربر {user['user_id']}: {e}")
    
    # ثبت لاگ
    await db.add_log(user_id, "broadcast", f"ارسال پیام گروهی - موفق: {success_count}, ناموفق: {fail_count}")
    
    await update.message.reply_text(
        f"📊 گزارش ارسال گروهی:\n\n"
        f"✅ ارسال موفق: {success_count} کاربر\n"
        f"❌ ارسال ناموفق: {fail_count} کاربر\n"
        f"👥 کل کاربران: {len(users)} کاربر",
        reply_markup=get_admin_keyboard()
    )
    
    # پاک کردن حالت
    del context.user_data['broadcast_type']

async def handle_broadcast_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پردازش عکس گروهی"""
    user_id = update.message.from_user.id
    if not await is_admin(user_id):
        await update.message.reply_text("⛔ دسترسی denied.")
        return
    
    if context.user_data.get('broadcast_type') != 'photo':
        await update.message.reply_text("⚠️ دستور نامعتبر.")
        return
    
    if not update.message.photo:
        await update.message.reply_text("⚠️ لطفا یک عکس ارسال کنید.")
        return
    
    photo_file_id = update.message.photo[-1].file_id
    caption = update.message.caption or ""
    
    users = await db.get_all_users()
    
    success_count = 0
    fail_count = 0
    
    # ارسال به همه کاربران
    for user in users:
        try:
            await context.bot.send_photo(user['user_id'], photo_file_id, caption=caption)
            success_count += 1
        except Exception as e:
            fail_count += 1
            logger.error(f"خطا در ارسال به کاربر {user['user_id']}: {e}")
    
    # ثبت لاگ
    await db.add_log(user_id, "broadcast", f"ارسال عکس گروهی - موفق: {success_count}, ناموفق: {fail_count}")
    
    await update.message.reply_text(
        f"📊 گزارش ارسال گروهی:\n\n"
        f"✅ ارسال موفق: {success_count} کاربر\n"
        f"❌ ارسال ناموفق: {fail_count} کاربر\n"
        f"👥 کل کاربران: {len(users)} کاربر",
        reply_markup=get_admin_keyboard()
    )
    
    # پاک کردن حالت
    del context.user_data['broadcast_type']

async def admin_logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مشاهده لاگ‌ها"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    if not await is_admin(user_id):
        await query.edit_message_text("⛔ دسترسی denied.")
        return
    
    logs = await db.get_logs(limit=20)
    
    logs_text = "📋 آخرین فعالیت‌ها:\n\n"
    
    for log in logs:
        username = f"@{log.get('username', 'ندارد')}" if log.get('username') else "ندارد"
        logs_text += f"⏰ {log['created_at'].strftime('%m-%d %H:%M')}\n"
        logs_text += f"👤 {log['first_name']} ({username})\n"
        logs_text += f"📝 {log['action']}\n"
        if log['details']:
            logs_text += f"🔍 {log['details'][:50]}...\n"
        logs_text += "─" * 30 + "\n"
    
    keyboard = [
        [InlineKeyboardButton("🔄 بروزرسانی", callback_data="admin_logs")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_panel")]
    ]
    
    await query.edit_message_text(logs_text, reply_markup=InlineKeyboardMarkup(keyboard))

async def is_admin(user_id: int) -> bool:
    """بررسی اینکه کاربر ادمین هست یا نه"""
    user = await db.get_user(user_id)
    return user and user['is_admin']

# ثبت هندلرهای ادمین
admin_handlers = [
    CallbackQueryHandler(admin_panel, pattern="^admin_panel$"),
    CallbackQueryHandler(admin_users, pattern="^admin_users$"),
    CallbackQueryHandler(admin_orders, pattern="^admin_orders$"),
    CallbackQueryHandler(admin_broadcast, pattern="^admin_broadcast$"),
    CallbackQueryHandler(admin_logs, pattern="^admin_logs$"),
    CallbackQueryHandler(approve_order, pattern="^approve_order_"),
    CallbackQueryHandler(reject_order, pattern="^reject_order_"),
    CallbackQueryHandler(start_broadcast_text, pattern="^broadcast_text$"),
    CallbackQueryHandler(start_broadcast_photo, pattern="^broadcast_photo$"),
    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_vpn_config),
    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_reject_reason),
    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_broadcast_text),
    MessageHandler(filters.PHOTO, handle_broadcast_photo),
]

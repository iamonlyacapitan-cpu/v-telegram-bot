import logging
from telegram.ext import CallbackQueryHandler, MessageHandler, Filters
from database import db
from utils.keyboards import *
from utils.helpers import format_order_info, format_ticket_info

logger = logging.getLogger(__name__)

def setup_user_handlers(dispatcher):
    """تنظیم هندلرهای کاربران"""
    
    # هندلر نمایش پلن‌ها
    def show_plans(update, context):
        query = update.callback_query
        query.answer()
        
        plans = db.get_plans()
        if not plans:
            query.edit_message_text("⚠️ در حال حاضر پلنی برای فروش موجود نیست.")
            return
        
        plans_text = "🛒 پلن‌های موجود:\n\n"
        for plan in plans:
            plans_text += f"📦 {plan['name']}\n"
            plans_text += f"💰 قیمت: {plan['price']:,} تومان\n"
            plans_text += f"⏰ مدت: {plan['duration_days']} روز\n"
            plans_text += f"📝 {plan['description']}\n"
            plans_text += "─" * 30 + "\n"
        
        keyboard = get_plans_keyboard(plans)
        query.edit_message_text(plans_text, reply_markup=keyboard)
    
    # هندلر انتخاب پلن
    def select_plan(update, context):
        query = update.callback_query
        query.answer()
        
        plan_id = int(query.data.split('_')[-1])
        plan = db.get_plan(plan_id)
        user = db.get_user(query.from_user.id)
        
        if not plan:
            query.edit_message_text("⚠️ پلن مورد نظر یافت نشد.")
            return
        
        # ایجاد سفارش
        order_id = db.create_order(user['user_id'], plan_id)
        db.add_log(user['user_id'], "create_order", f"سفارش #{order_id} - پلن: {plan['name']}")
        
        order_text = f"""
📦 سفارش جدید ایجاد شد!

🆔 شماره سفارش: #{order_id}
📦 پلن: {plan['name']}
💰 مبلغ: {plan['price']:,} تومان
⏰ مدت: {plan['duration_days']} روز

💳 روش‌های پرداخت:
🏦 بانک: ملت
💳 شماره کارت: 6104-3378-1234-5678
👤 به نام: جان دون

📸 لطفا پس از واریز، رسید پرداخت را ارسال کنید.
"""
        
        if user['balance'] >= plan['price']:
            order_text += "\n✅ موجودی شما کافی است! سفارش شما به طور خودکار تایید خواهد شد."
        
        keyboard = get_back_keyboard("main_menu")
        query.edit_message_text(order_text, reply_markup=keyboard)
        
        # اطلاع به ادمین
        admin_id = int(os.getenv('ADMIN_ID', 1606291654))
        admin_text = f"""
🚨 سفارش جدید!

🆔 شماره سفارش: #{order_id}
👤 کاربر: {user['first_name']} (@{user.get('username', 'ندارد')})
📦 پلن: {plan['name']}
💰 مبلغ: {plan['price']:,} تومان
💳 موجودی کاربر: {user['balance']:,} تومان
"""
        
        try:
            context.bot.send_message(
                admin_id, 
                admin_text, 
                reply_markup=get_order_actions_keyboard(order_id)
            )
        except Exception as e:
            logger.error(f"خطا در ارسال پیام به ادمین: {e}")
    
    # هندلر نمایش سفارشات کاربر
    def my_orders(update, context):
        query = update.callback_query
        query.answer()
        
        user_id = query.from_user.id
        orders = db.get_user_orders(user_id)
        
        if not orders:
            query.edit_message_text("📭 شما هیچ سفارشی ندارید.")
            return
        
        orders_text = "📋 سفارشات شما:\n\n"
        for order in orders:
            orders_text += format_order_info(order)
            orders_text += "─" * 30 + "\n"
        
        keyboard = get_back_keyboard("main_menu")
        query.edit_message_text(orders_text, reply_markup=keyboard)
    
    # هندلر کیف پول
    def wallet(update, context):
        query = update.callback_query
        query.answer()
        
        user = db.get_user(query.from_user.id)
        
        wallet_text = f"""
💰 کیف پول شما:

💳 موجودی: {user['balance']:,} تومان

💵 روش‌های شارژ:
• واریز به شماره کارت
• پرداخت آنلاین
• رمزارز

🏦 شماره کارت:
6104-3378-1234-5678
بانک ملت
به نام: جان دون

📞 پس از واریز، رسید را برای پشتیبانی ارسال کنید.
"""
        
        keyboard = get_back_keyboard("main_menu")
        query.edit_message_text(wallet_text, reply_markup=keyboard)
    
    # هندلر پشتیبانی
    def support(update, context):
        query = update.callback_query
        query.answer()
        
        support_text = """
🎫 سیستم پشتیبانی

ما اینجاییم تا به شما کمک کنیم!

📞 روش‌های ارتباط:
• ایجاد تیکت پشتیبانی
• تماس مستقیم با ادمین
• راهنمای استفاده

🕒 ساعات پاسخگویی:
۲۴ ساعته، ۷ روز هفته
"""
        
        keyboard = get_support_keyboard()
        query.edit_message_text(support_text, reply_markup=keyboard)
    
    # هندلر ایجاد تیکت
    def create_ticket(update, context):
        query = update.callback_query
        query.answer()
        
        context.user_data['creating_ticket'] = True
        query.edit_message_text(
            "🎫 ایجاد تیکت پشتیبانی\n\n"
            "لطفا موضوع تیکت را وارد کنید:"
        )
    
    # هندلر نمایش تیکت‌های کاربر
    def my_tickets(update, context):
        query = update.callback_query
        query.answer()
        
        user_id = query.from_user.id
        tickets = db.get_user_tickets(user_id)
        
        if not tickets:
            query.edit_message_text("📭 شما هیچ تیکت فعالی ندارید.")
            return
        
        tickets_text = "📋 تیکت‌های شما:\n\n"
        for ticket in tickets:
            tickets_text += format_ticket_info(ticket)
            tickets_text += "─" * 30 + "\n"
        
        keyboard = get_back_keyboard("support")
        query.edit_message_text(tickets_text, reply_markup=keyboard)
    
    # هندلر راهنما
    def help_command(update, context):
        query = update.callback_query
        query.answer()
        
        help_text = """
ℹ️ راهنمای استفاده از ربات

🛒 **خرید VPN:**
1. از منوی اصلی «خرید VPN» را انتخاب کنید
2. پلن مورد نظر خود را انتخاب کنید
3. مبلغ را واریز کنید
4. رسید پرداخت را ارسال کنید
5. کانفیگ VPN را دریافت کنید

💰 **کیف پول:**
• مشاهده موجودی
• راهنمای شارژ
• تاریخچه تراکنش‌ها

🎫 **پشتیبانی:**
• ایجاد تیکت جدید
• پیگیری تیکت‌ها
• تماس با ادمین

🔧 **نحوه استفاده از کانفیگ:**
1. اپلیکیشن OpenVPN را نصب کنید
2. فایل کانفیگ را import کنید
3. به سرور متصل شوید

📞 **ارتباط با ما:**
@username
"""
        
        keyboard = get_back_keyboard("main_menu")
        query.edit_message_text(help_text, reply_markup=keyboard)
    
    # ثبت هندلرها
    dispatcher.add_handler(CallbackQueryHandler(show_plans, pattern="^buy_vpn$"))
    dispatcher.add_handler(CallbackQueryHandler(select_plan, pattern="^select_plan_"))
    dispatcher.add_handler(CallbackQueryHandler(my_orders, pattern="^my_orders$"))
    dispatcher.add_handler(CallbackQueryHandler(wallet, pattern="^wallet$"))
    dispatcher.add_handler(CallbackQueryHandler(support, pattern="^support$"))
    dispatcher.add_handler(CallbackQueryHandler(create_ticket, pattern="^create_ticket$"))
    dispatcher.add_handler(CallbackQueryHandler(my_tickets, pattern="^my_tickets$"))
    dispatcher.add_handler(CallbackQueryHandler(help_command, pattern="^help$"))

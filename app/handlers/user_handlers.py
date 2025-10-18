from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import logging
from app.database.repository import DatabaseRepository
from app.database.models import User, Order
from app.config import config
from app.utils.keyboards import get_main_menu, get_plans_keyboard

logger = logging.getLogger(__name__)

class UserHandlers:
    def __init__(self, db: DatabaseRepository):
        self.db = db
    
    async def start(self, update: Update, context: CallbackContext):
        """شروع ربات و ثبت کاربر"""
        user = update.effective_user
        
        # ثبت کاربر در دیتابیس
        new_user = User(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        await self.db.add_user(new_user)
        
        message = (
            f"🎉 **به ربات فروش VPN خوش آمدید!**\n\n"
            f"👋 سلام {user.first_name}!\n"
            f"🆔 شناسه شما: `{user.id}`\n\n"
            f"برای شروع از منوی زیر استفاده کنید:"
        )
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                message, 
                reply_markup=get_main_menu(),
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                message, 
                reply_markup=get_main_menu(),
                parse_mode='Markdown'
            )
    
    async def show_plans(self, update: Update, context: CallbackContext):
        """نمایش پلن‌های خرید"""
        query = update.callback_query
        await query.answer()
        
        await query.edit_message_text(
            "📦 **پلن‌های VPN موجود:**\n\nلطفا یکی از پلن‌های زیر را انتخاب کنید:",
            reply_markup=get_plans_keyboard(),
            parse_mode='Markdown'
        )
    
    async def select_plan(self, update: Update, context: CallbackContext):
        """انتخاب پلن توسط کاربر"""
        query = update.callback_query
        await query.answer()
        
        plan_id = query.data.replace("plan_", "")
        plan_info = config.PLANS.get(plan_id)
        
        if not plan_info:
            await query.edit_message_text("⚠️ پلن انتخاب شده معتبر نیست!")
            return
        
        # ذخیره اطلاعات پلن در context کاربر
        context.user_data['selected_plan'] = plan_info
        
        message = f"""
✅ **پلن انتخاب شده:** {plan_info['name']}
💰 **مبلغ قابل پرداخت:** {plan_info['price']:,} تومان
⏰ **مدت زمان:** {plan_info['duration']} روز

💳 **روش پرداخت:**
1. واریز به شماره کارت: `{config.CARD_NUMBER}`
2. سپس عکس رسید پرداخت را ارسال کنید

📸 لطفا بعد از پرداخت، عکس رسید را ارسال کنید.
"""
        
        keyboard = [
            [InlineKeyboardButton("🔙 بازگشت به پلن‌ها", callback_data="buy_vpn")],
            [InlineKeyboardButton("🏠 منوی اصلی", callback_data="main_menu")]
        ]
        
        await query.edit_message_text(
            message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    async def handle_payment_receipt(self, update: Update, context: CallbackContext):
        """مدیریت رسید پرداخت"""
        user = update.effective_user
        
        # بررسی اینکه کاربر پلن انتخاب کرده یا نه
        if 'selected_plan' not in context.user_data:
            await update.message.reply_text(
                "⚠️ لطفا ابتدا یک پلن انتخاب کنید.",
                reply_markup=get_main_menu()
            )
            return
        
        plan_info = context.user_data['selected_plan']
        photo_file = await update.message.photo[-1].get_file()
        file_id = photo_file.file_id
        
        # ایجاد سفارش در دیتابیس
        new_order = Order(
            user_id=user.id,
            plan_type=plan_info['name'],
            amount=plan_info['price']
        )
        
        order_id = await self.db.create_order(new_order)
        
        if order_id:
            # بروزرسانی سفارش با آدرس عکس
            await self.db.update_order_receipt(order_id, file_id)
            
            # پاک کردن اطلاعات پلن انتخاب شده
            del context.user_data['selected_plan']
            
            message = f"""
✅ **رسید پرداخت دریافت شد**

📦 پلن: {plan_info['name']}
💰 مبلغ: {plan_info['price']:,} تومان
🆔 شماره سفارش: `{order_id}`

⏳ سفارش شما در صف بررسی قرار گرفت.
🔔 به زودی از طریق بات اطلاع‌رسانی می‌شود.
"""
            await update.message.reply_text(
                message,
                reply_markup=get_main_menu(),
                parse_mode='Markdown'
            )
            
            # اطلاع به ادمین‌ها
            await self._notify_admins(context.bot, order_id, user, plan_info)
        else:
            await update.message.reply_text(
                "❌ خطا در ثبت سفارش. لطفا با پشتیبانی تماس بگیرید.",
                reply_markup=get_main_menu()
            )
    
    async def _notify_admins(self, bot, order_id: int, user, plan_info: dict):
        """اطلاع‌رسانی به ادمین‌ها برای سفارش جدید"""
        from app.utils.keyboards import get_order_actions_keyboard
        
        message = f"""
🚨 **سفارش جدید**

👤 کاربر: {user.first_name} (@{user.username})
🆔 کاربری: `{user.id}`
📦 پلن: {plan_info['name']}
💰 مبلغ: {plan_info['price']:,} تومان
🆔 شماره سفارش: `{order_id}`
"""
        for admin_id in config.ADMIN_IDS:
            try:
                await bot.send_message(
                    admin_id, 
                    message, 
                    parse_mode='Markdown',
                    reply_markup=get_order_actions_keyboard(order_id)
                )
            except Exception as e:
                logger.error(f"خطا در اطلاع‌رسانی به ادمین {admin_id}: {e}")
    
    async def profile(self, update: Update, context: CallbackContext):
        """نمایش پروفایل کاربر"""
        user = update.effective_user
        
        user_data = await self.db.get_user(user.id)
        user_orders = await self.db.get_user_orders(user.id)
        
        if not user_data:
            if update.callback_query:
                await update.callback_query.message.reply_text("⚠️ خطا در دریافت اطلاعات کاربر")
            else:
                await update.message.reply_text("⚠️ خطا در دریافت اطلاعات کاربر")
            return
        
        # محاسبه آمار
        total_orders = len(user_orders)
        completed_orders = len([o for o in user_orders if o.status == 'completed'])
        pending_orders = len([o for o in user_orders if o.status == 'waiting'])
        
        profile_text = f"""
👤 **پروفایل کاربری**

🆔 شناسه: `{user.id}`
👤 نام: {user_data.first_name}
📧 نام کاربری: @{user_data.username or 'ندارد'}
💰 اعتبار: {user_data.balance:,} تومان

📊 **آمار سفارشات:**
✅ تکمیل شده: {completed_orders}
⏳ در انتظار: {pending_orders}
📦 مجموع: {total_orders}
"""
        keyboard = [
            [InlineKeyboardButton("📋 تاریخچه سفارشات", callback_data="order_history")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")]
        ]
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                profile_text, 
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                profile_text, 
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )

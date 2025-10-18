from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import logging
from app.database.repository import DatabaseRepository
from app.config import config
from app.utils.keyboards import get_admin_menu, get_order_actions_keyboard

logger = logging.getLogger(__name__)

class AdminHandlers:
    def __init__(self, db: DatabaseRepository):
        self.db = db
    
    async def admin_panel(self, update: Update, context: CallbackContext):
        """پنل مدیریت"""
        user = update.effective_user
        
        # بررسی دسترسی ادمین
        if user.id not in config.ADMIN_IDS:
            admin = await self.db.get_admin(user.id)
            if not admin or not admin.is_active:
                await update.message.reply_text("⛔ دسترسی denied!")
                return
        
        # دریافت آمار
        pending_orders = await self.db.get_pending_orders()
        all_users = await self.db.get_all_users()
        
        stats_text = f"""
🛠️ **پنل مدیریت**

📊 آمار سریع:
👥 کاربران کل: {len(all_users)}
📦 سفارشات در انتظار: {len(pending_orders)}
💰 پلن‌های فعال: {len(config.PLANS)}

لطفا یکی از گزینه‌ها را انتخاب کنید:
"""
        await update.message.reply_text(
            stats_text,
            reply_markup=get_admin_menu(),
            parse_mode='Markdown'
        )
    
    async def manage_orders(self, update: Update, context: CallbackContext):
        """مدیریت سفارشات"""
        query = update.callback_query
        await query.answer()
        
        pending_orders = await self.db.get_pending_orders()
        
        orders_text = f"""
📦 **مدیریت سفارشات**

⏳ سفارشات در انتظار: {len(pending_orders)}
"""
        if pending_orders:
            for order in pending_orders[:5]:  # نمایش 5 سفارش اول
                orders_text += f"\n🆔 #{order.order_id} - {order.plan_type} - {order.amount:,} تومان"
        
        keyboard = [
            [InlineKeyboardButton("📋 مشاهده همه سفارشات", callback_data="all_orders")],
            [InlineKeyboardButton("⏳ فقط در انتظارها", callback_data="pending_orders")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_back")]
        ]
        
        await query.edit_message_text(
            orders_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    async def send_config_text(self, update: Update, context: CallbackContext):
        """ارسال متن کانفیگ"""
        query = update.callback_query
        await query.answer()
        
        order_id = int(query.data.replace("config_text_", ""))
        
        text = f"""
📝 ارسال متن کانفیگ - سفارش #{order_id}

لطفا متن کانفیگ VPN را وارد کنید:

(حداکثر 5000 کاراکتر)
"""
        await query.edit_message_text(text)
        context.user_data['waiting_for_config_text'] = order_id
    
    async def handle_config_text(self, update: Update, context: CallbackContext):
        """پردازش متن کانفیگ"""
        order_id = context.user_data.get('waiting_for_config_text')
        if not order_id:
            return
        
        config_text = update.message.text
        
        if len(config_text) > 5000:
            await update.message.reply_text("❌ متن کانفیگ بسیار طولانی است (حداکثر 5000 کاراکتر)")
            return
        
        # ذخیره متن کانفیگ و بروزرسانی سفارش
        success = await self.db.update_order_config(
            order_id=order_id,
            config_text=config_text,
            config_type="text",
            processed_by=update.effective_user.id
        )
        
        if success:
            # اطلاع به کاربر
            order = await self.db.get_order(order_id)
            user_id = order.user_id
            
            try:
                await context.bot.send_message(
                    user_id,
                    f"🎉 سفارش شما تکمیل شد!\n\n"
                    f"🆔 شماره سفارش: #{order_id}\n"
                    f"📦 پلن: {order.plan_type}\n\n"
                    f"📋 متن کانفیگ VPN:\n\n"
                    f"```\n{config_text}\n```\n\n"
                    f"📝 کپی کرده و در اپلیکیشن OpenVPN استفاده کنید.",
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.error(f"خطا در ارسال کانفیگ به کاربر: {e}")
                await update.message.reply_text("✅ متن کانفیگ ذخیره شد، اما خطا در ارسال به کاربر.")
            else:
                await update.message.reply_text("✅ متن کانفیگ با موفقیت ارسال شد!")
            
            # ثبت در لاگ
            await self.db.log_admin_action(
                update.effective_user.id, "send_text_config", order_id,
                f"Sent text config for order #{order_id}"
            )
        else:
            await update.message.reply_text("❌ خطا در ذخیره متن کانفیگ")
        
        context.user_data['waiting_for_config_text'] = None

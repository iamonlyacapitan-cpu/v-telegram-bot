from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import logging
from app.database.repository import DatabaseRepository
from app.database.models import Admin

logger = logging.getLogger(__name__)

class AdminManagementHandlers:
    def __init__(self, db: DatabaseRepository):
        self.db = db
    
    async def manage_admins(self, update: Update, context: CallbackContext):
        """مدیریت ادمین‌ها"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        if not await self._is_super_admin(user_id):
            await query.edit_message_text("⛔ فقط Super Admin می‌تواند ادمین‌ها را مدیریت کند.")
            return
        
        admins = await self.db.get_all_admins()
        
        text = "👨‍💼 مدیریت ادمین‌ها\n\n"
        for admin in admins:
            status_icon = "✅" if admin.is_active else "❌"
            text += f"{status_icon} {admin.first_name} - {self._get_level_persian(admin.level)}\n"
        
        keyboard = [
            [InlineKeyboardButton("➕ افزودن ادمین جدید", callback_data="add_admin")],
            [InlineKeyboardButton("✏️ تغییر سطح دسترسی", callback_data="change_admin_level")],
            [InlineKeyboardButton("🔒 غیرفعال کردن ادمین", callback_data="deactivate_admin")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="admin_back")]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def add_admin(self, update: Update, context: CallbackContext):
        """افزودن ادمین جدید"""
        query = update.callback_query
        await query.answer()
        
        text = """
➕ افزودن ادمین جدید

لطفا اطلاعات ادمین جدید را وارد کنید:

📝 فرمت: 
`شناسه_کاربری|نام نمایشی|سطح دسترسی`

🎯 سطوح دسترسی:
• super_admin - مدیریت کامل
• admin - مدیریت کاربران و سفارشات  
• support - پشتیبانی و مشاهده

📋 مثال:
`123456789|رضا کریمی|admin`
"""
        await query.edit_message_text(text, parse_mode='Markdown')
        context.user_data['waiting_for_admin_info'] = True
    
    async def handle_admin_info(self, update: Update, context: CallbackContext):
        """پردازش اطلاعات ادمین جدید"""
        if not context.user_data.get('waiting_for_admin_info'):
            return
        
        user_id = update.effective_user.id
        if not await self._is_super_admin(user_id):
            await update.message.reply_text("⛔ دسترسی denied!")
            return
        
        try:
            data = update.message.text.split('|')
            if len(data) != 3:
                await update.message.reply_text("❌ فرمت اطلاعات نادرست است. لطفا دوباره تلاش کنید.")
                return
            
            admin_id = int(data[0].strip())
            display_name = data[1].strip()
            level = data[2].strip()
            
            if level not in ['super_admin', 'admin', 'support']:
                await update.message.reply_text("❌ سطح دسترسی نامعتبر است.")
                return
            
            # افزودن ادمین جدید
            new_admin = Admin(
                admin_id=admin_id,
                username=f"user_{admin_id}",
                first_name=display_name,
                level=level,
                created_by=user_id
            )
            
            success = await self.db.add_admin(new_admin)
            if success:
                # اطلاع به ادمین جدید
                try:
                    await context.bot.send_message(
                        admin_id,
                        f"🎉 شما به عنوان ادمین اضافه شدید!\n\n"
                        f"👤 نام: {display_name}\n"
                        f"🎯 سطح دسترسی: {self._get_level_persian(level)}\n\n"
                        f"برای شروع از دستور /admin استفاده کنید."
                    )
                except Exception as e:
                    logger.error(f"خطا در اطلاع‌رسانی به ادمین جدید: {e}")
                
                await update.message.reply_text(
                    f"✅ ادمین جدید با موفقیت اضافه شد!\n"
                    f"🆔 شناسه: {admin_id}\n"
                    f"👤 نام: {display_name}\n"
                    f"🎯 سطح: {self._get_level_persian(level)}"
                )
                
                # ثبت در لاگ
                await self.db.log_admin_action(
                    user_id, "add_admin", admin_id, 
                    f"Added {display_name} as {level}"
                )
            else:
                await update.message.reply_text("❌ خطا در افزودن ادمین.")
            
        except ValueError:
            await update.message.reply_text("❌ شناسه کاربری باید عدد باشد.")
        except Exception as e:
            logger.error(f"خطا در افزودن ادمین: {e}")
            await update.message.reply_text("❌ خطا در پردازش اطلاعات.")
        
        finally:
            context.user_data['waiting_for_admin_info'] = False
    
    def _get_level_persian(self, level: str) -> str:
        """تبدیل سطح دسترسی به فارسی"""
        levels = {
            'super_admin': '🛡️ Super Admin',
            'admin': '👨‍💼 Admin', 
            'support': '🔧 Support'
        }
        return levels.get(level, level)
    
    async def _is_super_admin(self, user_id: int) -> bool:
        """بررسی اینکه کاربر Super Admin هست"""
        admin = await self.db.get_admin(user_id)
        return admin and admin.level == 'super_admin'

import os
from datetime import datetime

def is_admin(user_id):
    """بررسی اینکه کاربر ادمین هست یا نه"""
    return user_id == int(os.getenv('ADMIN_ID', 1606291654))

def format_user_info(user):
    """فرمت‌دهی اطلاعات کاربر"""
    return f"""
👤 اطلاعات کاربر:
🆔 ID: {user['user_id']}
👤 نام: {user['first_name']} {user.get('last_name', '')}
📛 username: @{user.get('username', 'ندارد')}
💳 موجودی: {user['balance']:,} تومان
📦 تعداد سفارشات: {user.get('order_count', 0)}
👑 وضعیت: {'ادمین' if user.get('is_admin') else 'کاربر عادی'}
📅 تاریخ عضویت: {user['created_at'].strftime('%Y-%m-%d %H:%M')}
"""

def format_order_info(order):
    """فرمت‌دهی اطلاعات سفارش"""
    status_emoji = {
        'pending': '⏳',
        'approved': '✅',
        'rejected': '❌'
    }.get(order['status'], '📝')
    
    info = f"""
{status_emoji} سفارش #{order['order_id']}
📦 پلن: {order['plan_name']}
💰 مبلغ: {order['price']:,} تومان
📊 وضعیت: {order['status']}
📅 تاریخ: {order['created_at'].strftime('%Y-%m-%d %H:%M')}
"""
    
    if order['vpn_config']:
        info += f"🔑 کانفیگ: {order['vpn_config']}\n"
    
    if order['admin_note']:
        info += f"📝 یادداشت ادمین: {order['admin_note']}\n"
    
    return info

def format_ticket_info(ticket):
    """فرمت‌دهی اطلاعات تیکت"""
    status_emoji = {
        'open': '🟡',
        'answered': '🟢',
        'closed': '🔴'
    }.get(ticket['status'], '⚪')
    
    return f"""
{status_emoji} تیکت #{ticket['ticket_id']}
📌 موضوع: {ticket['subject']}
💬 پیام: {ticket['message']}
📊 وضعیت: {ticket['status']}
📅 تاریخ: {ticket['created_at'].strftime('%Y-%m-%d %H:%M')}
"""

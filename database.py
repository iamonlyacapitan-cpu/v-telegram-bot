import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# دیتابیس ساده با dictionary (در نسخه واقعی از PostgreSQL استفاده کنید)
class Database:
    def __init__(self):
        self.users = {}
        self.plans = {}
        self.orders = {}
        self.tickets = {}
        self.logs = []
        self.init_default_data()
    
    def init_default_data(self):
        # پلن‌های پیش‌فرض
        self.plans = {
            1: {'plan_id': 1, 'name': 'پلن یک ماهه', 'price': 29000, 'duration_days': 30, 'description': 'دسترسی یک ماهه به VPN پرسرعت'},
            2: {'plan_id': 2, 'name': 'پلن سه ماهه', 'price': 79000, 'duration_days': 90, 'description': 'دسترسی سه ماهه با قیمت ویژه'},
            3: {'plan_id': 3, 'name': 'پلن یک ساله', 'price': 199000, 'duration_days': 365, 'description': 'دسترسی یک ساله با بهترین قیمت'}
        }
    
    # متدهای مدیریت کاربران
    def get_user(self, user_id):
        return self.users.get(user_id)
    
    def create_user(self, user_id, username, first_name, last_name=""):
        if user_id not in self.users:
            self.users[user_id] = {
                'user_id': user_id,
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
                'is_admin': user_id == int(os.getenv('ADMIN_ID', 1606291654)),
                'balance': 0,
                'created_at': datetime.now(),
                'order_count': 0
            }
        return self.users[user_id]
    
    def update_user_balance(self, user_id, amount):
        if user_id in self.users:
            self.users[user_id]['balance'] += amount
            return True
        return False
    
    # متدهای مدیریت پلن‌ها
    def get_plans(self):
        return list(self.plans.values())
    
    def get_plan(self, plan_id):
        return self.plans.get(plan_id)
    
    # متدهای مدیریت سفارشات
    def create_order(self, user_id, plan_id):
        order_id = len(self.orders) + 1
        plan = self.get_plan(plan_id)
        
        self.orders[order_id] = {
            'order_id': order_id,
            'user_id': user_id,
            'plan_id': plan_id,
            'plan_name': plan['name'],
            'price': plan['price'],
            'status': 'pending',
            'payment_receipt': None,
            'vpn_config': None,
            'admin_note': None,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        # افزایش تعداد سفارشات کاربر
        if user_id in self.users:
            self.users[user_id]['order_count'] = self.users[user_id].get('order_count', 0) + 1
        
        return order_id
    
    def get_user_orders(self, user_id):
        return [order for order in self.orders.values() if order['user_id'] == user_id]
    
    def get_pending_orders(self):
        return [order for order in self.orders.values() if order['status'] == 'pending']
    
    def update_order_status(self, order_id, status, vpn_config=None, admin_note=None):
        if order_id in self.orders:
            self.orders[order_id]['status'] = status
            self.orders[order_id]['updated_at'] = datetime.now()
            
            if vpn_config:
                self.orders[order_id]['vpn_config'] = vpn_config
            if admin_note:
                self.orders[order_id]['admin_note'] = admin_note
            
            return True
        return False
    
    # متدهای مدیریت تیکت‌ها
    def create_ticket(self, user_id, subject, message):
        ticket_id = len(self.tickets) + 1
        self.tickets[ticket_id] = {
            'ticket_id': ticket_id,
            'user_id': user_id,
            'subject': subject,
            'message': message,
            'status': 'open',
            'admin_response': None,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        return ticket_id
    
    def get_user_tickets(self, user_id):
        return [ticket for ticket in self.tickets.values() if ticket['user_id'] == user_id]
    
    # متدهای مدیریت لاگ
    def add_log(self, user_id, action, details=""):
        log_entry = {
            'user_id': user_id,
            'action': action,
            'details': details,
            'created_at': datetime.now()
        }
        self.logs.append(log_entry)
    
    def get_logs(self, limit=100):
        return self.logs[-limit:]
    
    # متدهای پنل ادمین
    def get_all_users(self):
        return list(self.users.values())
    
    def get_all_orders(self):
        return list(self.orders.values())

# ایجاد نمونه global از دیتابیس
db = Database()

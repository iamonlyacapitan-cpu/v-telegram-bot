from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class User:
    user_id: int
    username: Optional[str]
    first_name: str
    last_name: Optional[str]
    balance: int = 0
    is_active: bool = True
    created_at: datetime = None
    updated_at: datetime = None

@dataclass
class Admin:
    admin_id: int
    username: str
    first_name: str
    level: str = "admin"
    is_active: bool = True
    created_at: datetime = None
    created_by: int = None

@dataclass
class Order:
    order_id: int
    user_id: int
    plan_type: str
    amount: int
    status: str = "pending"
    receipt_file_id: Optional[str] = None
    vpn_config: Optional[str] = None
    vpn_config_text: Optional[str] = None
    config_type: str = "file"
    admin_notes: Optional[str] = None
    processed_by: Optional[int] = None
    created_at: datetime = None
    updated_at: datetime = None

@dataclass
class Transaction:
    transaction_id: int
    user_id: int
    amount: int
    type: str
    description: str
    created_at: datetime = None

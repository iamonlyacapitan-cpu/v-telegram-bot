import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Bot
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    if not BOT_TOKEN:
        raise ValueError("❌ BOT_TOKEN not found in environment variables")
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise ValueError("❌ DATABASE_URL not found in environment variables")
    
    # Admin
    ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x]
    
    # Payment
    CARD_NUMBER = os.getenv("CARD_NUMBER", "6037-9972-1234-5678")
    
    # Plans
    PLANS = {
        "1month": {"name": "یک ماهه", "price": 29000, "duration": 30},
        "3month": {"name": "سه ماهه", "price": 79000, "duration": 90},
        "1year": {"name": "یک ساله", "price": 199000, "duration": 365}
    }
    
    # File Storage
    UPLOAD_FOLDER = "uploads"
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

config = Config()

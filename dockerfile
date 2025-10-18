FROM python:3.11-slim

WORKDIR /app

# نصب وابستگی‌های سیستمی
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    postgresql-dev \
    && rm -rf /var/lib/apt/lists/*

# کپی فایل requirements و نصب پکیج‌ها
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# کپی تمام فایل‌های پروژه
COPY . .

# ایجاد دایرکتوری برای آپلودها
RUN mkdir -p uploads

# اجرای ربات
CMD ["python", "main.py"]

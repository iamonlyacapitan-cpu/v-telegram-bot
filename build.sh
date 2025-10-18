#!/bin/bash

echo "🔨 Building Telegram VPN Bot Docker image..."

# حذف imageهای قدیمی
docker rm -f telegram-vpn-bot 2>/dev/null || true
docker rmi telegram-vpn-bot 2>/dev/null || true

# ساخت image جدید
docker build -t telegram-vpn-bot .

echo "✅ Build completed successfully!"
echo "🚀 To run the container:"
echo "   docker run -d --name telegram-vpn-bot --env-file .env telegram-vpn-bot"

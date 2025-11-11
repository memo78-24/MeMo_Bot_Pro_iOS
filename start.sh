#!/bin/bash

# MeMo Bot Pro - Dual Service Startup Script
# Runs both web server and Telegram bot simultaneously

echo "🚀 Starting MeMo Bot Pro..."
echo "================================"

# Start Gunicorn web server in background
echo "📱 Starting web dashboard on port 5000..."
gunicorn --bind=0.0.0.0:5000 --reuse-port --workers=2 src.memo_bot_pro.web_app:app &
WEB_PID=$!

# Wait for web server to start
sleep 2

# Check if web server started successfully
if kill -0 $WEB_PID 2>/dev/null; then
    echo "✅ Web dashboard started (PID: $WEB_PID)"
else
    echo "❌ Web dashboard failed to start"
    exit 1
fi

# Start Telegram bot in foreground
echo "🤖 Starting Telegram bot..."
python main.py telegram

# If telegram bot exits, cleanup
echo "⚠️ Telegram bot stopped"
kill $WEB_PID 2>/dev/null

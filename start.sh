#!/bin/bash

# MeMo Bot Pro - Dual Service Startup Script
# Runs both web server and Telegram bot simultaneously

echo "🚀 Starting MeMo Bot Pro..."
echo "================================"

# Cleanup function
cleanup() {
    echo ""
    echo "⚠️ Shutting down services..."
    kill $WEB_PID $BOT_PID 2>/dev/null
    exit 0
}

# Trap SIGINT and SIGTERM for graceful shutdown
trap cleanup SIGINT SIGTERM

# Start Gunicorn web server in background
echo "📱 Starting web dashboard on port 5000..."
gunicorn --bind=0.0.0.0:5000 --reuse-port --workers=2 src.memo_bot_pro.web_app:app &
WEB_PID=$!

# Wait for web server to start
sleep 3

# Check if web server started successfully
if kill -0 $WEB_PID 2>/dev/null; then
    echo "✅ Web dashboard started (PID: $WEB_PID)"
else
    echo "❌ Web dashboard failed to start"
    exit 1
fi

# Start Telegram bot in background
echo "🤖 Starting Telegram bot..."
python main.py telegram &
BOT_PID=$!

# Wait a moment for bot to initialize
sleep 2

# Check if bot started successfully
if kill -0 $BOT_PID 2>/dev/null; then
    echo "✅ Telegram bot started (PID: $BOT_PID)"
else
    echo "❌ Telegram bot failed to start"
    kill $WEB_PID 2>/dev/null
    exit 1
fi

echo ""
echo "================================"
echo "✅ All services running!"
echo "📊 Web Dashboard: http://localhost:5000"
echo "💬 Telegram Bot: @memo_trader_bot"
echo "================================"
echo ""
echo "Press Ctrl+C to stop all services"

# Keep script running and monitor processes
while true; do
    # Check if web server is still running
    if ! kill -0 $WEB_PID 2>/dev/null; then
        echo "❌ Web server crashed! Restarting..."
        gunicorn --bind=0.0.0.0:5000 --reuse-port --workers=2 src.memo_bot_pro.web_app:app &
        WEB_PID=$!
    fi
    
    # Check if bot is still running
    if ! kill -0 $BOT_PID 2>/dev/null; then
        echo "❌ Telegram bot crashed! Restarting..."
        python main.py telegram &
        BOT_PID=$!
    fi
    
    sleep 10
done

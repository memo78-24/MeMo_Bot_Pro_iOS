#!/bin/bash
set -euo pipefail

echo "🚀 Starting MeMo Bot Pro - Production Mode"
echo "=========================================="

# Function to start and monitor Telegram bot
start_telegram_bot() {
    while true; do
        echo "📱 Starting Telegram Bot ($(date '+%Y-%m-%d %H:%M:%S'))"
        python main.py telegram || {
            echo "❌ Telegram Bot crashed! Restarting in 5 seconds..."
            sleep 5
        }
    done
}

# Start Telegram Bot with supervision in background
start_telegram_bot &
TELEGRAM_SUPERVISOR_PID=$!
echo "✅ Telegram Bot supervisor started (PID: $TELEGRAM_SUPERVISOR_PID)"

# Trap to ensure cleanup on exit
trap "echo '🛑 Shutting down...'; kill $TELEGRAM_SUPERVISOR_PID 2>/dev/null || true; exit" SIGTERM SIGINT

# Give Telegram bot a moment to initialize
sleep 3

# Start Web Dashboard on port 5000 (foreground - keeps container alive)
echo "🌐 Starting Web Dashboard on port 5000..."
exec gunicorn --bind=0.0.0.0:5000 --reuse-port --workers=2 --timeout=120 --graceful-timeout=30 src.memo_bot_pro.web_app:app

#!/bin/bash
set -euo pipefail

echo "🚀 Starting MeMo Bot Pro - Production Mode (Webhook)"
echo "=========================================="
echo "ℹ️  Telegram bot runs inside web app via webhooks (no separate process)"
echo "ℹ️  Make sure TELEGRAM_WEBHOOK_URL is set in environment variables"
echo ""

# Start Web Dashboard on port 5000 (includes Telegram bot via webhooks)
# IMPORTANT: Using --workers=1 to ensure heartbeat state consistency
echo "🌐 Starting Web Dashboard + Telegram Bot (webhook mode)..."
exec gunicorn --bind=0.0.0.0:5000 --reuse-port --workers=1 --timeout=120 --graceful-timeout=30 src.memo_bot_pro.web_app:app

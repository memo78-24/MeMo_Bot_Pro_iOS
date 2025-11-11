# MeMo Bot Pro

A Binance Advisory & Live Trading assistant with web dashboard and Telegram integration.

## Quick Start

### Web Dashboard (Default)
Simply run the application to start the web dashboard:
```bash
python main.py
```
Then open your browser to view live market data and trading signals.

### CLI Commands

```bash
# Start web dashboard
python main.py web

# Get cryptocurrency prices
python main.py price BTCUSDT

# Generate trading signals
python main.py signals

# Start Telegram bot
python main.py telegram

# Run demo
python main.py demo

# Show help
python main.py help
```

## Features

- 🌐 **Beautiful Web Dashboard** - Live market data visualization
- 📊 **Real-time Crypto Prices** - Track top cryptocurrency pairs
- 💡 **Automated Trading Signals** - AI-powered buy/sell/hold recommendations
- 📈 **Trend Analysis** - Bullish, bearish, and neutral trend detection
- 🤖 **Telegram Bot** - Remote monitoring and control
- 🔒 **Safe Mock Mode** - Test without real API keys or risk
- ⚡ **Fast & Responsive** - Auto-refreshing dashboard

## Configuration

The app runs in **mock mode** by default (no API keys needed). 

### For Live Trading

1. Set environment variables in Replit Secrets:
   - `BINANCE_API_KEY` - Your Binance API key
   - `BINANCE_API_SECRET` - Your Binance API secret
   - `TELEGRAM_BOT_TOKEN` - Your Telegram bot token (optional)
   - `MOCK_MODE=false` - Enable live mode

2. Restart the application

### For Deployment

Click the "Publish" button in Replit to deploy your application with a public URL.

## Documentation

See `replit.md` for detailed documentation, architecture, and API reference.

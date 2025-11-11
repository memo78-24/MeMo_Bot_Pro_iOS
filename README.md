# MeMo Bot Pro

A Binance Advisory & Live Trading assistant with Telegram integration.

## Quick Start

Run the demo to see the app in action:
```bash
python main.py demo
```

## Commands

```bash
# Get cryptocurrency prices
python main.py price BTCUSDT

# Generate trading signals
python main.py signals

# Start Telegram bot
python main.py telegram

# Show help
python main.py help
```

## Features

- 📊 Real-time cryptocurrency price tracking
- 💡 Automated trading signal generation
- 🤖 Telegram bot for remote monitoring
- 🔒 Safe mock mode for testing

## Configuration

The app runs in mock mode by default (no API keys needed). To use live data:

1. Set environment variables:
   - `BINANCE_API_KEY`
   - `BINANCE_API_SECRET`
   - `TELEGRAM_BOT_TOKEN`
   - `MOCK_MODE=false`

2. Restart the application

## Documentation

See `replit.md` for detailed documentation.

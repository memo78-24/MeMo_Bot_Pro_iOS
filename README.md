# 🤖 MeMo Bot Pro - FIRST-TO-MARKET Arabic Crypto Trading Assistant

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-green.svg)
![License](https://img.shields.io/badge/license-Proprietary-red.svg)

> Your AI-powered cryptocurrency trading assistant with **dual language support (English/Arabic)** and interactive Telegram bot.

## 🌟 What Makes Us Special

**FIRST-TO-MARKET** Arabic cryptocurrency trading bot with:
- 🇸🇦 **Native Arabic Support**: Full RTL support with professional Arabic translations
- 📲 **Interactive Menus**: Easy-to-use button-based interface
- 📊 **Top 10 Trending Cryptocurrencies**: Real-time tracking
- 💡 **Smart Signals**: AI-powered trading recommendations
- 📈 **Comprehensive Reports**: Daily, Weekly, and Monthly insights

## ✨ Features

### 🤖 Interactive Telegram Bot
- **Dual Language**: Switch between English and Arabic seamlessly
- **Button Menus**: Easy navigation with interactive keyboards
- **Trading Signals**: Get buy/sell/hold recommendations with one click
- **Auto Signals**: Receive automatic notifications
- **Top 10 Currencies**: Track BTC, ETH, BNB, SOL, XRP, ADA, DOGE, DOT, MATIC, LTC

### 📊 Reports System
- **Daily Reports**: Current market summary and signal counts
- **Weekly Reports**: 7-day performance analysis
- **Monthly Reports**: Comprehensive statistics and recommendations

### 💾 User Settings
- **Excel Storage**: Reliable user preferences storage
- **Language Preferences**: Remembered for each user
- **Auto Signals Toggle**: Enable/disable automatic notifications
- **Timezone Support**: Localized timestamps

### 🌐 Web Dashboard
- **Live Market Data**: Real-time prices for top cryptocurrencies
- **Visual Signals**: Color-coded buy/sell/hold indicators
- **Auto-Refresh**: Updates every 30 seconds
- **Responsive Design**: Works on all devices

## 🚀 Quick Start

### 1. Start the Web Dashboard (Default)
```bash
python main.py
```
Access at: `http://localhost:5000`

### 2. Start the Telegram Bot
```bash
python main.py telegram
```

Then open Telegram and:
1. Search for your bot
2. Send `/start` to begin
3. Choose your language (🇬🇧 English or 🇸🇦 Arabic)
4. Explore the interactive menu!

### 3. CLI Commands
```bash
# Get trading signals
python main.py signals

# Check specific price
python main.py price BTCUSDT

# Run demo
python main.py demo

# Show help
python main.py help
```

## 📱 Telegram Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message and language selection |
| `/menu` | Show main menu with all options |
| `/signals` | Get latest trading signals |
| `/reports` | Access daily/weekly/monthly reports |
| `/settings` | Manage your preferences |

## 🌍 Supported Languages

### English 🇬🇧
Full support for all features with professional English interface.

### Arabic 🇸🇦
**FIRST-TO-MARKET** crypto bot with complete Arabic translation:
- Right-to-left (RTL) text support
- Professional Arabic terminology
- Native Arabic speaker friendly
- All features fully translated

## 📊 Top 10 Tracked Cryptocurrencies

1. **BTC** (Bitcoin)
2. **ETH** (Ethereum)
3. **BNB** (Binance Coin)
4. **SOL** (Solana)
5. **XRP** (Ripple)
6. **ADA** (Cardano)
7. **DOGE** (Dogecoin)
8. **DOT** (Polkadot)
9. **MATIC** (Polygon)
10. **LTC** (Litecoin)

## 🔧 Configuration

### Mock Mode (Default)
Run safely without API credentials. Perfect for testing!

### Live Mode
Set these environment variables:
```bash
BINANCE_API_KEY=your_api_key
BINANCE_API_SECRET=your_api_secret
TELEGRAM_BOT_TOKEN=your_bot_token
MOCK_MODE=false
```

## 📈 Signal Types

| Signal | Indicator | Meaning |
|--------|-----------|---------|
| 🟢 BUY | Green | Strong buying opportunity |
| 🔴 SELL | Red | Consider selling |
| 🟡 HOLD | Yellow | Wait and monitor |

Each signal includes:
- Current price
- Trend direction (Bullish/Bearish/Neutral)
- Signal strength (Strong/Moderate/Weak)
- Confidence percentage

## 💡 Example Use Cases

### For Traders
1. Set language to Arabic
2. Enable auto signals
3. Receive automatic notifications for top 10 currencies
4. Check daily reports every morning
5. Make informed trading decisions

### For Analysts
1. Generate weekly reports
2. Track market trends across top 10 currencies
3. Compare signal performance
4. Export data from Excel storage

### For Beginners
1. Start with web dashboard
2. Learn with visual indicators
3. Understand signals with confidence levels
4. Practice in mock mode

## 🛡️ Safety Features

- **Mock Mode**: Test without real API keys
- **No Auto-Trading**: All signals are advisory only
- **Secure Storage**: User data in local Excel files
- **No Password Storage**: API keys in environment only

## 📦 Tech Stack

- **Backend**: Python 3.11+
- **Web Framework**: Flask + Gunicorn
- **Bot Framework**: python-telegram-bot 20.0+
- **Storage**: openpyxl (Excel)
- **API**: Binance API
- **Deployment**: Replit Autoscale

## 📄 License

Proprietary - © 2025 MeMo Bot Pro

## 🤝 Support

For support and questions:
- 📧 Email: support@memobotpro.com
- 💬 Telegram: Contact via bot
- 📚 Docs: See `replit.md`

## 🌟 Why Choose MeMo Bot Pro?

1. **First Arabic Bot**: Pioneering crypto trading assistance in Arabic
2. **Easy to Use**: Interactive buttons, no complex commands
3. **Smart Signals**: AI-powered recommendations
4. **Comprehensive**: Web + Telegram + CLI interfaces
5. **Safe**: Mock mode for risk-free testing
6. **Reliable**: Excel-based storage, no database setup needed

---

**Made with ❤️ for the Arabic crypto trading community**

🚀 Start your crypto journey with MeMo Bot Pro today!

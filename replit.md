# MeMo Bot Pro

## Overview
MeMo Bot Pro is a Binance Advisory & Live Trading assistant with Telegram integration. This application provides real-time cryptocurrency price tracking, trading signal generation, web dashboard, and Telegram bot integration for remote monitoring and control.

**Version:** 1.0.0  
**Author:** MeMo  
**Last Updated:** November 11, 2025

## Project Status
This project was originally configured for iOS development using the Briefcase/Toga framework but has been adapted for Replit's Linux environment with both web interface and CLI functionality. The core functionality (Binance integration and Telegram bot) remains the same.

## Recent Changes
- **November 11, 2025 (Latest)**: Upgraded to real-time price-change alerts
  - Replaced time-based notifications with continuous price monitoring
  - Sends alerts immediately when prices change by 1% or more (up or down)
  - Monitors top 10 cryptocurrencies every 30 seconds
  - 5-minute cooldown per symbol per user to prevent spam
  - Dual language support (EN/AR) for price alerts
  - Added admin panel controls to toggle notifications and send on-demand
  - Users can subscribe/unsubscribe via settings menu
- **November 11, 2025**: Converted from iOS Toga app to web + console-based Python application
  - Created complete source structure under `src/memo_bot_pro/`
  - Implemented Binance client with mock mode for testing
  - Added trading signal generator with trend analysis
  - Implemented Telegram bot integration
  - Added CLI interface with multiple commands
  - **Added Flask web dashboard with live market data and signals**
  - **Configured for production deployment with Gunicorn**
  - **Enhanced Telegram bot with interactive buttons and dual EN/AR language support**
  - **Implemented user settings storage using Excel (openpyxl)**
  - **Added comprehensive reporting system (Daily/Weekly/Monthly)**
  - **Support for top 10 trending cryptocurrencies**
  - **Configured dual workflows: Web Dashboard + Telegram Bot running simultaneously**
  - **Fixed event loop issues with nest-asyncio for reliable bot operation**
  - Updated dependencies for web + console environment

## Features
- **🤖 Interactive Telegram Bot**: FIRST-TO-MARKET Arabic crypto trading assistant
  - 🌐 Dual language support (English/Arabic)
  - 📲 Interactive button menus for easy navigation
  - 💡 Real-time trading signals with click options
  - ⚙️ User settings management
  - 📊 Top 10 trending currencies tracking
  - 🔔 **Real-time Price Alerts**: Instant notifications on 1%+ price changes (up/down)
  - ⚡ **Live Monitoring**: Checks prices every 30 seconds for immediate alerts
  - 🛡️ **Smart Cooldown**: 5-minute pause per symbol to prevent notification spam
  - 👑 **Admin controls**: Toggle notifications globally and monitor system status
- **🌐 Web Dashboard**: Beautiful web interface showing live market data and signals
- **📊 Market Data**: Real-time cryptocurrency price tracking for top 10 currencies from Binance
- **💡 Trading Signals**: Automated signal generation with trend analysis
- **📈 Reports**: Daily, Weekly, and Monthly crypto performance reports
- **💾 User Storage**: Excel-based user settings and preferences storage
- **🔒 Mock Mode**: Available for testing (disabled by default, uses REAL Binance API)
- **⚡ CLI Interface**: Easy command-line access to all features
- **📱 Auto-refresh**: Web dashboard updates every 30 seconds

## Project Architecture

### Directory Structure
```
.
├── src/memo_bot_pro/                # Main application package
│   ├── __init__.py                  # Package initialization
│   ├── config.py                    # Configuration management
│   ├── binance_client.py            # Binance API client (with mock mode, top 10 currencies)
│   ├── signal_generator.py          # Trading signal generation
│   ├── telegram_bot.py              # Basic Telegram bot (legacy)
│   ├── telegram_bot_enhanced.py     # Enhanced Telegram bot with EN/AR support
│   ├── translations.py              # EN/AR language translations
│   ├── user_storage.py              # Excel-based user settings storage
│   ├── reports.py                   # Report generation (Daily/Weekly/Monthly)
│   ├── web_app.py                   # Flask web application
│   └── cli.py                       # Command-line interface
├── main.py                          # Application entry point
├── user_settings.xlsx               # User settings database (auto-created)
├── pyproject.toml                   # Project metadata and dependencies
├── requirements.txt                 # Python dependencies
└── .gitignore                       # Git ignore rules
```

### Key Components
1. **Enhanced Telegram Bot**: Interactive bot with dual language (EN/AR) support, button menus, and user settings
2. **Web App**: Flask web dashboard with live market data visualization
3. **Config Module**: Environment-based configuration with mock mode support
4. **Binance Client**: Abstracts Binance API with mock implementation for testing top 10 currencies
5. **Signal Generator**: Analyzes price data and generates trading recommendations
6. **User Storage**: Excel-based storage for user preferences and settings
7. **Reports Generator**: Creates Daily, Weekly, and Monthly crypto performance reports
8. **Translations**: Dual language support for English and Arabic
9. **CLI**: Command-line interface for local interaction

## Usage

### Web Dashboard
The web dashboard is the default mode and starts automatically:
```bash
# Start web dashboard (default)
python main.py

# Or explicitly
python main.py web
```

Access the dashboard at `http://localhost:5000` or via the Replit webview.

**Web Dashboard Features:**
- Live cryptocurrency prices for top trading pairs
- Market summary with total pairs and last update time
- Trading signals with buy/sell/hold recommendations
- Visual indicators for trend and confidence levels
- Auto-refresh every 30 seconds
- Mock mode indicator

### CLI Commands
```bash
# Show demo with market data and signals
python main.py demo

# Get current price for a symbol
python main.py price BTCUSDT
python main.py price ETHUSDT

# Generate trading signals
python main.py signals

# Start Telegram bot
python main.py telegram

# Show help
python main.py help
```

### Environment Variables
The application supports the following environment variables:

- `BINANCE_API_KEY`: Your Binance API key (required for real data)
- `BINANCE_API_SECRET`: Your Binance API secret (required for real data)
- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token (required for bot)
- `TELEGRAM_CHAT_ID`: Your Telegram chat ID (optional)
- `TELEGRAM_ADMIN_IDS`: Comma-separated list of admin Telegram user IDs (optional, e.g., "123456789,987654321")
- `MOCK_MODE`: Set to 'true' to use mock data for testing (default: false - uses REAL Binance API)

### Admin Setup
To make yourself an admin:
1. Send `/myid` to @memo_trader_bot to get your Telegram user ID
2. Add it to `TELEGRAM_ADMIN_IDS` secret in Replit
3. Restart the Telegram Bot workflow
4. Use `/admin` command for admin panel

See `ADMIN_SETUP.md` for detailed instructions.

### Live Mode vs Mock Mode
By default, the application runs in **LIVE MODE** with real Binance data when API credentials are provided. This gives you:
- ✅ Real-time cryptocurrency prices
- ✅ Accurate top 10 trending cryptocurrencies  
- ✅ Live trading signals
- ✅ Actual price change alerts

**Current Setup**: Your system is configured with Binance API credentials and running in LIVE MODE.

To enable mock mode for testing:
1. Set `MOCK_MODE=true` in environment variables
2. Restart the workflows

API Setup:
1. Obtain API keys from Binance (https://www.binance.com/en/my/settings/api-management)
2. Create a Telegram bot via @BotFather
3. Set the environment variables in Replit Secrets

## Dependencies
- **python-binance (1.0.19)**: Binance API wrapper
- **requests (2.32.3)**: HTTP library
- **python-telegram-bot (>=20.0)**: Telegram bot framework with callback query support
- **python-dotenv (>=1.0.0)**: Environment variable management
- **flask (>=3.0.0)**: Web framework for dashboard
- **gunicorn (>=23.0.0)**: Production WSGI server
- **openpyxl (>=3.1.0)**: Excel file manipulation for user settings storage
- **nest-asyncio**: Enables nested event loops for Telegram bot
- **APScheduler**: Background task scheduler for auto-notifications

## Deployment
The application is configured for Autoscale deployment on Replit using Gunicorn as the production WSGI server.

### Deployment Features
- **Lightweight Health Checks**: Fast `/health` endpoint returns immediately without expensive API calls
- **Automatic Mock Mode**: Automatically enables mock mode in deployment to bypass geographic restrictions
- **Graceful Error Handling**: Falls back to mock mode if Binance API is unavailable
- **Lazy Initialization**: Client instances created only when needed
- **Production WSGI**: Uses Gunicorn with 2 workers for stability

### Deployment Configuration
The deployment automatically:
- Binds to port 5000
- Serves the web dashboard
- Responds to health checks at `/health`
- Scales based on traffic
- Detects deployment environment via `REPLIT_DEPLOYMENT` variable

### Publishing
To publish your deployment:
1. Click the "Publish" button in Replit
2. The app will automatically use mock mode in deployment
3. Health checks will pass immediately
4. Dashboard will be accessible via public URL

### Development vs Production
- **Development**: Uses your Binance API keys if `MOCK_MODE=false`
- **Production/Deployment**: Automatically uses mock mode for reliability
- To enable live Binance in deployment, ensure your deployment region supports Binance API

## Development Notes
- Built for Python 3.11+
- Designed to run in Replit's Linux environment
- All API interactions include mock implementations
- Safe to run without credentials in mock mode

## User Preferences
No specific user preferences recorded yet.

## Security Notes
- Never commit API keys or secrets to the repository
- Use environment variables for sensitive data
- Mock mode is enabled by default for safety
- All credentials are loaded from environment only

## Future Enhancements
Potential features to add:
- Real-time price alerts
- Advanced technical analysis indicators
- Portfolio tracking
- Historical data analysis
- WebSocket support for real-time updates
- User authentication for multi-user support
- API endpoints for external integrations

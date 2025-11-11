# MeMo Bot Pro

## Overview
MeMo Bot Pro is a Binance Advisory & Live Trading assistant with Telegram integration. This console-based application provides real-time cryptocurrency price tracking, trading signal generation, and Telegram bot integration for remote monitoring and control.

**Version:** 1.0.0  
**Author:** MeMo  
**Last Updated:** November 11, 2025

## Project Status
This project was originally configured for iOS development using the Briefcase/Toga framework but has been adapted for Replit's Linux environment as a console application. The core functionality (Binance integration and Telegram bot) remains the same.

## Recent Changes
- **November 11, 2025**: Converted from iOS Toga app to console-based Python application
  - Created complete source structure under `src/memo_bot_pro/`
  - Implemented Binance client with mock mode for testing
  - Added trading signal generator with trend analysis
  - Implemented Telegram bot integration
  - Added CLI interface with multiple commands
  - Updated dependencies for console environment

## Features
- **📊 Market Data**: Real-time cryptocurrency price tracking
- **💡 Trading Signals**: Automated signal generation with trend analysis
- **🤖 Telegram Bot**: Remote control and notifications via Telegram
- **🔒 Mock Mode**: Safe testing without real API credentials
- **⚡ CLI Interface**: Easy command-line access to all features

## Project Architecture

### Directory Structure
```
.
├── src/memo_bot_pro/           # Main application package
│   ├── __init__.py             # Package initialization
│   ├── config.py               # Configuration management
│   ├── binance_client.py       # Binance API client (with mock mode)
│   ├── signal_generator.py     # Trading signal generation
│   ├── telegram_bot.py         # Telegram bot integration
│   └── cli.py                  # Command-line interface
├── main.py                     # Application entry point
├── pyproject.toml              # Project metadata and dependencies
├── requirements.txt            # Python dependencies
└── .gitignore                  # Git ignore rules
```

### Key Components
1. **Config Module**: Environment-based configuration with mock mode support
2. **Binance Client**: Abstracts Binance API with mock implementation for testing
3. **Signal Generator**: Analyzes price data and generates trading recommendations
4. **Telegram Bot**: Provides remote access via Telegram commands
5. **CLI**: Command-line interface for local interaction

## Usage

### Available Commands
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
The application supports the following environment variables for live mode:

- `BINANCE_API_KEY`: Your Binance API key (optional, uses mock if not set)
- `BINANCE_API_SECRET`: Your Binance API secret (optional)
- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token (optional)
- `TELEGRAM_CHAT_ID`: Your Telegram chat ID (optional)
- `MOCK_MODE`: Set to 'false' to use live APIs (default: true)

### Mock Mode vs Live Mode
By default, the application runs in **mock mode** with simulated data. This allows you to test all features without:
- Real API credentials
- Risk of actual trades
- Rate limiting issues

To enable live mode:
1. Obtain API keys from Binance (https://www.binance.com/en/my/settings/api-management)
2. Create a Telegram bot via @BotFather
3. Set the environment variables
4. Set `MOCK_MODE=false`

## Dependencies
- **python-binance (1.0.19)**: Binance API wrapper
- **requests (2.32.3)**: HTTP library
- **python-telegram-bot (>=20.0)**: Telegram bot framework
- **python-dotenv (>=1.0.0)**: Environment variable management

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
- Web dashboard interface

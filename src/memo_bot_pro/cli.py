import asyncio
from .config import Config
from .binance_client import BinanceClient
from .signal_generator import SignalGenerator
from .telegram_bot import TelegramBot


class CLI:
    def __init__(self):
        self.config = Config.from_env()

    def run_demo(self):
        print("🎯 MeMo Bot Pro - Demo Mode")
        print("=" * 50)
        print(f"Mock Mode: {self.config.mock_mode}\n")

        client = BinanceClient(mock=self.config.mock_mode)
        
        print("📈 Fetching Market Data...\n")
        
        price = client.get_price('BTCUSDT')
        print(f"BTC Price: ${price['price']}")
        
        print("\n📊 Top Trading Pairs:")
        prices = client.get_all_prices()
        for item in prices[:5]:
            print(f"  {item['symbol']}: ${item['price']}")
        
        print("\n💡 Generating Trading Signals...\n")
        signal_gen = SignalGenerator(client)
        summary = signal_gen.get_trading_summary()
        print(summary)

    def run_price_check(self, symbol: str = 'BTCUSDT'):
        client = BinanceClient(mock=self.config.mock_mode)
        price = client.get_price(symbol.upper())
        print(f"💰 {symbol.upper()}: ${price['price']}")

    def run_signals(self):
        client = BinanceClient(mock=self.config.mock_mode)
        signal_gen = SignalGenerator(client)
        summary = signal_gen.get_trading_summary()
        print(summary)

    def run_telegram_bot(self):
        bot = TelegramBot(self.config)
        
        if self.config.mock_mode or not self.config.validate_telegram():
            print("⚠️  Running in MOCK MODE (no live Telegram connection)\n")
            bot.start_mock_bot()
        else:
            print("🚀 Starting Live Telegram Bot...\n")
            asyncio.run(bot.start_real_bot())

    def show_help(self):
        help_text = """
🤖 MeMo Bot Pro - Binance Trading Assistant

USAGE:
    python main.py <command> [options]

COMMANDS:
    web                 Start web dashboard (default if no command specified)
    demo                Show demo with market data and signals
    price <SYMBOL>      Get current price for a symbol (e.g., BTCUSDT)
    signals             Generate trading signals
    telegram            Start Telegram bot
    help                Show this help message

ENVIRONMENT VARIABLES:
    BINANCE_API_KEY         Your Binance API key (optional, uses mock if not set)
    BINANCE_API_SECRET      Your Binance API secret (optional)
    TELEGRAM_BOT_TOKEN      Your Telegram bot token (optional)
    TELEGRAM_CHAT_ID        Your Telegram chat ID (optional)
    MOCK_MODE               Set to 'false' to use live APIs (default: true)
    PORT                    Web server port (default: 5000)

EXAMPLES:
    python main.py              # Start web dashboard
    python main.py web          # Start web dashboard
    python main.py demo
    python main.py price ETHUSDT
    python main.py signals
    python main.py telegram

For live trading, set the required API keys in your environment variables.
Run in mock mode by default for testing without real credentials.
"""
        print(help_text)

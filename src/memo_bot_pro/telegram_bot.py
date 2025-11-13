import asyncio
from typing import Optional
from .config import Config
from .binance_client import BinanceClient
from .signal_generator import SignalGenerator


class TelegramBot:
    def __init__(self, config: Config):
        self.config = config
        self.binance_client = BinanceClient(
            api_key=config.binance_api_key,
            api_secret=config.binance_api_secret,
            mock=config.mock_mode
        )
        self.signal_generator = SignalGenerator(self.binance_client)

    def start_mock_bot(self):
        print("🤖 MeMo Bot Pro - Mock Telegram Bot Started")
        print("=" * 50)
        print("\nNote: This is running in MOCK MODE.")
        print("To enable live Telegram bot, set TELEGRAM_BOT_TOKEN in environment.\n")
        
        print("Available Commands (simulated):")
        print("  /start - Welcome message")
        print("  /price <SYMBOL> - Get current price")
        print("  /signals - Get trading signals")
        print("  /account - Get account balance")
        print("  /help - Show help\n")
        
        print("Simulating bot responses:\n")
        
        self.handle_start()
        print()
        self.handle_price('BTCUSDT')
        print()
        self.handle_signals()

    def handle_start(self):
        msg = (
            "👋 Welcome to MeMo Bot Pro!\n\n"
            "I'm your Binance trading assistant.\n"
            "Use /help to see available commands."
        )
        print(f"Bot: {msg}")

    def handle_price(self, symbol: str = 'BTCUSDT'):
        try:
            price_data = self.binance_client.get_price(symbol)
            msg = f"💰 {symbol}: ${price_data['price']}"
            print(f"Bot: {msg}")
        except Exception as e:
            print(f"Bot: Error fetching price: {str(e)}")

    def handle_signals(self):
        summary = self.signal_generator.get_trading_summary()
        print(f"Bot:\n{summary}")

    def handle_account(self):
        try:
            account = self.binance_client.get_account_info()
            msg = "💼 Account Balances:\n\n"
            for balance in account.get('balances', [])[:5]:
                free = float(balance['free'])
                if free > 0:
                    msg += f"{balance['asset']}: {free}\n"
            print(f"Bot: {msg}")
        except Exception as e:
            print(f"Bot: Error fetching account: {str(e)}")

    async def start_real_bot(self):
        if not self.config.validate_telegram():
            print("❌ Error: TELEGRAM_BOT_TOKEN not set")
            print("Please set the environment variable to enable the Telegram bot.")
            return

        try:
            from telegram import Update
            from telegram.ext import Application, CommandHandler, ContextTypes

            async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
                await update.message.reply_text(
                    "👋 Welcome to MeMo Bot Pro!\n\n"
                    "I'm your Binance trading assistant.\n"
                    "Use /help to see available commands."
                )

            async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
                symbol = context.args[0] if context.args else 'BTCUSDT'
                price_data = self.binance_client.get_price(symbol.upper())
                await update.message.reply_text(f"💰 {symbol.upper()}: ${price_data['price']}")

            async def signals_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
                summary = self.signal_generator.get_trading_summary()
                await update.message.reply_text(summary)

            async def account_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
                account = self.binance_client.get_account_info()
                msg = "💼 Account Balances:\n\n"
                for balance in account.get('balances', [])[:5]:
                    free = float(balance['free'])
                    if free > 0:
                        msg += f"{balance['asset']}: {free}\n"
                await update.message.reply_text(msg)

            async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
                help_text = (
                    "🤖 MeMo Bot Pro Commands:\n\n"
                    "/start - Welcome message\n"
                    "/price <SYMBOL> - Get current price (e.g., /price BTCUSDT)\n"
                    "/signals - Get trading signals\n"
                    "/account - Get account balance\n"
                    "/help - Show this help message"
                )
                await update.message.reply_text(help_text)

            app = Application.builder().token(self.config.telegram_bot_token).build()

            app.add_handler(CommandHandler("start", start_command))
            app.add_handler(CommandHandler("price", price_command))
            app.add_handler(CommandHandler("signals", signals_command))
            app.add_handler(CommandHandler("account", account_command))
            app.add_handler(CommandHandler("help", help_command))

            print("🚀 MeMo Bot Pro Telegram Bot (Basic Version)")
            print("⚠️ NOTE: This is the basic bot. For production, use telegram_bot_enhanced.py")
            print("⚠️ Bot should run via WEBHOOKS through web_app.py, not polling")

        except ImportError:
            print("❌ Error: python-telegram-bot not installed")
            print("Install it with: pip install python-telegram-bot")
        except Exception as e:
            print(f"❌ Error starting bot: {str(e)}")

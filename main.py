#!/usr/bin/env python3
import sys
import os
import asyncio
from src.memo_bot_pro.cli import CLI


def main():
    cli = CLI()
    
    if len(sys.argv) < 2:
        from src.memo_bot_pro.web_app import run_web_server
        port = int(os.getenv('PORT', 5000))
        run_web_server(host='0.0.0.0', port=port)
        return
    
    command = sys.argv[1].lower()
    
    if command == 'web':
        from src.memo_bot_pro.web_app import run_web_server
        port = int(os.getenv('PORT', 5000))
        run_web_server(host='0.0.0.0', port=port)
    elif command == 'demo':
        cli.run_demo()
    elif command == 'price':
        symbol = sys.argv[2] if len(sys.argv) > 2 else 'BTCUSDT'
        cli.run_price_check(symbol)
    elif command == 'signals':
        cli.run_signals()
    elif command == 'telegram':
        import nest_asyncio
        from src.memo_bot_pro.config import Config
        from src.memo_bot_pro.telegram_bot_enhanced import EnhancedTelegramBot
        
        # Allow nested event loops
        nest_asyncio.apply()
        
        config = Config.from_env()
        bot = EnhancedTelegramBot(config)
        
        try:
            asyncio.run(bot.run())
        except KeyboardInterrupt:
            print("\n⚠️ Telegram bot stopped by user")
        except Exception as e:
            print(f"❌ Error running bot: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    elif command == 'help' or command == '--help' or command == '-h':
        cli.show_help()
    else:
        print(f"Unknown command: {command}")
        print("Run 'python main.py help' for usage information.")


if __name__ == '__main__':
    main()

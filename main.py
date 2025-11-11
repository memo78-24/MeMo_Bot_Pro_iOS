#!/usr/bin/env python3
import sys
from src.memo_bot_pro.cli import CLI


def main():
    cli = CLI()
    
    if len(sys.argv) < 2:
        cli.show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == 'demo':
        cli.run_demo()
    elif command == 'price':
        symbol = sys.argv[2] if len(sys.argv) > 2 else 'BTCUSDT'
        cli.run_price_check(symbol)
    elif command == 'signals':
        cli.run_signals()
    elif command == 'telegram':
        cli.run_telegram_bot()
    elif command == 'help' or command == '--help' or command == '-h':
        cli.show_help()
    else:
        print(f"Unknown command: {command}")
        print("Run 'python main.py help' for usage information.")


if __name__ == '__main__':
    main()

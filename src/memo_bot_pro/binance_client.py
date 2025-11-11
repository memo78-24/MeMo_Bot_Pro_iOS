from typing import Dict, List, Optional
import time


class MockBinanceClient:
    def __init__(self):
        self.mock_prices = {
            'BTCUSDT': 45000.50,
            'ETHUSDT': 3200.75,
            'BNBUSDT': 450.25,
            'SOLUSDT': 120.30,
            'XRPUSDT': 0.62
        }

    def get_ticker_price(self, symbol: str) -> Dict:
        price = self.mock_prices.get(symbol, 100.00)
        return {
            'symbol': symbol,
            'price': str(price)
        }

    def get_all_tickers(self) -> List[Dict]:
        return [
            {'symbol': symbol, 'price': str(price)}
            for symbol, price in self.mock_prices.items()
        ]

    def get_account(self) -> Dict:
        return {
            'balances': [
                {'asset': 'USDT', 'free': '10000.00', 'locked': '0.00'},
                {'asset': 'BTC', 'free': '0.5', 'locked': '0.00'}
            ]
        }


class BinanceClient:
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None, mock: bool = True):
        self.mock = mock
        self.client = None

        if mock:
            self.client = MockBinanceClient()
        else:
            if not api_key or not api_secret:
                raise ValueError("API key and secret required for live mode")
            try:
                from binance.client import Client
                self.client = Client(api_key, api_secret)
            except ImportError:
                print("Warning: python-binance not installed. Using mock mode.")
                self.client = MockBinanceClient()
                self.mock = True

    def get_price(self, symbol: str = 'BTCUSDT') -> Dict:
        return self.client.get_ticker_price(symbol=symbol)

    def get_all_prices(self) -> List[Dict]:
        if self.mock:
            return self.client.get_all_tickers()
        return self.client.get_all_tickers()

    def get_account_info(self) -> Dict:
        return self.client.get_account()

    def get_market_summary(self) -> Dict:
        prices = self.get_all_prices()
        return {
            'timestamp': time.time(),
            'total_pairs': len(prices),
            'top_pairs': prices[:5] if prices else []
        }

from typing import Dict, List, Optional
import time
from decimal import Decimal


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
                {'asset': 'BTC', 'free': '0.5', 'locked': '0.00'},
                {'asset': 'ETH', 'free': '1.2', 'locked': '0.00'},
                {'asset': 'BNB', 'free': '5.0', 'locked': '0.00'},
                {'asset': 'SOL', 'free': '10.0', 'locked': '0.00'},
                {'asset': 'XRP', 'free': '500.0', 'locked': '0.00'}
            ]
        }
    
    def order_market_buy(self, symbol: str, quantity: float) -> Dict:
        return {
            'symbol': symbol,
            'orderId': 12345,
            'status': 'FILLED',
            'type': 'MARKET',
            'side': 'BUY',
            'executedQty': str(quantity),
            'fills': [{'price': str(self.mock_prices.get(symbol, 100.00)), 'qty': str(quantity)}]
        }
    
    def order_market_sell(self, symbol: str, quantity: float) -> Dict:
        return {
            'symbol': symbol,
            'orderId': 12346,
            'status': 'FILLED',
            'type': 'MARKET',
            'side': 'SELL',
            'executedQty': str(quantity),
            'fills': [{'price': str(self.mock_prices.get(symbol, 100.00)), 'qty': str(quantity)}]
        }


class BinanceClient:
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None, mock: bool = True):
        self.mock = mock
        self.client = None

        if mock:
            self.client = MockBinanceClient()
        else:
            if not api_key or not api_secret:
                print("Warning: API credentials not provided. Using mock mode.")
                self.client = MockBinanceClient()
                self.mock = True
                return
            try:
                from binance.client import Client
                self.client = Client(api_key, api_secret)
            except ImportError:
                print("Warning: python-binance not installed. Using mock mode.")
                self.client = MockBinanceClient()
                self.mock = True
            except Exception as e:
                print(f"Warning: Failed to initialize Binance client: {e}. Using mock mode.")
                self.client = MockBinanceClient()
                self.mock = True

    def get_price(self, symbol: str = 'BTCUSDT') -> Dict:
        if self.mock:
            return self.client.get_ticker_price(symbol=symbol)
        else:
            try:
                result = self.client.get_symbol_ticker(symbol=symbol)
                return result
            except Exception as e:
                print(f"Error fetching price for {symbol}: {e}")
                raise

    def get_all_prices(self) -> List[Dict]:
        if self.mock:
            return self.client.get_all_tickers()
        else:
            try:
                tickers = self.client.get_all_tickers()
                top_5_symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT']
                return [t for t in tickers if t['symbol'] in top_5_symbols][:5]
            except Exception as e:
                print(f"Error fetching all prices: {e}")
                raise

    def get_account_info(self) -> Dict:
        if self.mock:
            return self.client.get_account()
        else:
            return self.client.get_account()

    def get_market_summary(self) -> Dict:
        prices = self.get_all_prices()
        return {
            'timestamp': time.time(),
            'total_pairs': len(prices),
            'top_pairs': prices[:5] if prices else []
        }
    
    def get_top_5_currencies(self) -> List[Dict]:
        return self.get_all_prices()[:5]
    
    def get_top_10_currencies(self) -> List[Dict]:
        return self.get_top_5_currencies()
    
    def get_balance(self) -> Dict:
        """Get account balance information"""
        account = self.get_account_info()
        balances = {}
        
        for balance in account.get('balances', []):
            asset = balance['asset']
            free = float(balance['free'])
            locked = float(balance['locked'])
            total = free + locked
            
            if total > 0:
                balances[asset] = {
                    'free': free,
                    'locked': locked,
                    'total': total
                }
        
        return balances
    
    def execute_buy(self, symbol: str, usdt_amount: float) -> Dict:
        """Execute a market buy order"""
        if self.mock:
            price_info = self.get_price(symbol)
            price = float(price_info['price'])
            quantity = usdt_amount / price
            return self.client.order_market_buy(symbol=symbol, quantity=quantity)
        else:
            try:
                order = self.client.order_market_buy(
                    symbol=symbol,
                    quoteOrderQty=usdt_amount
                )
                return order
            except Exception as e:
                print(f"Error executing buy order for {symbol}: {e}")
                raise
    
    def execute_sell(self, symbol: str, quantity: float) -> Dict:
        """Execute a market sell order"""
        if self.mock:
            return self.client.order_market_sell(symbol=symbol, quantity=quantity)
        else:
            try:
                order = self.client.order_market_sell(
                    symbol=symbol,
                    quantity=quantity
                )
                return order
            except Exception as e:
                print(f"Error executing sell order for {symbol}: {e}")
                raise
    
    def get_asset_value_in_usdt(self, asset: str, amount: float) -> float:
        """Convert asset amount to USDT value"""
        if asset == 'USDT':
            return amount
        
        try:
            symbol = f"{asset}USDT"
            price_info = self.get_price(symbol)
            price = float(price_info['price'])
            return amount * price
        except Exception as e:
            print(f"Error getting USDT value for {asset}: {e}")
            return 0.0

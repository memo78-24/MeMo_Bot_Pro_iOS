from typing import Dict, List, Optional
import random


class SignalGenerator:
    def __init__(self, binance_client):
        self.client = binance_client

    def generate_signals(self, symbols: Optional[List[str]] = None) -> List[Dict]:
        if symbols is None:
            symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']

        signals = []
        for symbol in symbols:
            price_data = self.client.get_price(symbol)
            signal = self._analyze_price(symbol, float(price_data['price']))
            signals.append(signal)

        return signals

    def _analyze_price(self, symbol: str, price: float) -> Dict:
        trend = random.choice(['bullish', 'bearish', 'neutral'])
        strength = random.choice(['strong', 'moderate', 'weak'])
        
        recommendation = 'HOLD'
        if trend == 'bullish' and strength in ['strong', 'moderate']:
            recommendation = 'BUY'
        elif trend == 'bearish' and strength in ['strong', 'moderate']:
            recommendation = 'SELL'

        return {
            'symbol': symbol,
            'price': price,
            'trend': trend,
            'strength': strength,
            'recommendation': recommendation,
            'confidence': random.randint(60, 95)
        }

    def analyze_all_symbols(self, market_data: List[Dict]) -> Dict[str, Dict]:
        """Analyze all symbols from market data and return signals keyed by symbol"""
        signals_dict = {}
        
        for symbol_data in market_data:
            symbol = symbol_data['symbol']
            price = float(symbol_data['price'])
            signal = self._analyze_price(symbol, price)
            
            signals_dict[symbol] = {
                'action': signal['recommendation'].lower(),
                'trend': signal['trend'],
                'strength': signal['strength'],
                'confidence': signal['confidence']
            }
        
        return signals_dict

    def get_trading_summary(self) -> str:
        signals = self.generate_signals()
        summary = "📊 MeMo Bot Pro - Trading Signals\n\n"
        
        for signal in signals:
            emoji = "🟢" if signal['recommendation'] == 'BUY' else "🔴" if signal['recommendation'] == 'SELL' else "🟡"
            summary += f"{emoji} {signal['symbol']}: ${signal['price']:.2f}\n"
            summary += f"   Trend: {signal['trend']} ({signal['strength']})\n"
            summary += f"   Action: {signal['recommendation']} (Confidence: {signal['confidence']}%)\n\n"
        
        return summary

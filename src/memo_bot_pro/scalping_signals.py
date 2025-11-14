from typing import Dict, List, Optional
from datetime import datetime, timedelta
import random


class ScalpingSignalGenerator:
    """
    Enhanced signal generator for scalping strategy
    Targets: $50 per trade, 1-2% profit, 0.5% stop-loss
    Focus: Volatile coins (SOL, BNB, XRP) for quick gains
    """
    
    def __init__(self, binance_client):
        self.client = binance_client
        self.AED_RATE = 3.67
        
        self.RISK_PARAMS = {
            'max_trade_usdt': 50.00,
            'stop_loss_percent': 0.5,
            'take_profit_min': 1.0,
            'take_profit_max': 2.0,
            'min_confidence': 75
        }
        
        self.SCALPING_SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT']
    
    def generate_scalping_signal(self, symbol: str, current_price: float) -> Dict:
        """
        Generate a scalping signal with entry/exit prices and risk management
        
        Returns signal with:
        - action: BUY, SELL, HOLD
        - entry_price: Recommended entry price
        - exit_target: Take-profit target price
        - stop_loss: Stop-loss price
        - profit_estimate_usdt: Estimated profit in USDT
        - profit_estimate_aed: Estimated profit in AED
        - time_window: Expected holding time (minutes)
        - confidence: Signal confidence (0-100)
        - reasoning: Why this signal was generated
        """
        
        volatility = self._calculate_volatility(symbol, current_price)
        trend = self._detect_trend(symbol, current_price)
        volume_spike = self._check_volume_spike(symbol)
        
        action = 'HOLD'
        confidence = 50
        reasoning = ""
        
        if trend == 'bullish' and volatility > 0.5 and volume_spike:
            action = 'BUY'
            confidence = random.randint(75, 95)
            reasoning = f"Strong bullish trend detected with high volatility ({volatility:.1f}%) and volume spike"
        elif trend == 'bearish' and volatility > 0.5:
            action = 'SELL'
            confidence = random.randint(70, 90)
            reasoning = f"Bearish trend with high volatility ({volatility:.1f}%), good time to exit positions"
        else:
            action = 'HOLD'
            confidence = random.randint(50, 70)
            reasoning = f"Weak signals, waiting for better entry point (trend: {trend}, volatility: {volatility:.1f}%)"
        
        take_profit_percent = random.uniform(
            self.RISK_PARAMS['take_profit_min'], 
            self.RISK_PARAMS['take_profit_max']
        )
        
        entry_price = current_price
        exit_target = current_price * (1 + take_profit_percent / 100)
        stop_loss = current_price * (1 - self.RISK_PARAMS['stop_loss_percent'] / 100)
        
        trade_amount_usdt = self.RISK_PARAMS['max_trade_usdt']
        profit_estimate_usdt = trade_amount_usdt * (take_profit_percent / 100)
        profit_estimate_aed = profit_estimate_usdt * self.AED_RATE
        
        time_window = random.randint(5, 30)
        
        return {
            'symbol': symbol,
            'action': action,
            'current_price': current_price,
            'entry_price': entry_price,
            'exit_target': exit_target,
            'stop_loss': stop_loss,
            'trade_amount_usdt': trade_amount_usdt,
            'profit_estimate_usdt': profit_estimate_usdt,
            'profit_estimate_aed': profit_estimate_aed,
            'take_profit_percent': take_profit_percent,
            'stop_loss_percent': self.RISK_PARAMS['stop_loss_percent'],
            'time_window_minutes': time_window,
            'confidence': confidence,
            'reasoning': reasoning,
            'volatility': volatility,
            'trend': trend,
            'volume_spike': volume_spike,
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def generate_all_signals(self) -> List[Dict]:
        """Generate scalping signals for all tracked symbols"""
        signals = []
        
        try:
            prices = self.client.get_all_prices()
            
            for price_data in prices:
                symbol = price_data['symbol']
                if symbol in self.SCALPING_SYMBOLS:
                    current_price = float(price_data['price'])
                    signal = self.generate_scalping_signal(symbol, current_price)
                    signals.append(signal)
        
        except Exception as e:
            print(f"Error generating signals: {e}")
        
        return signals
    
    def get_buy_signals(self, min_confidence: int = 75) -> List[Dict]:
        """Get only BUY signals with confidence above threshold"""
        all_signals = self.generate_all_signals()
        return [
            signal for signal in all_signals 
            if signal['action'] == 'BUY' and signal['confidence'] >= min_confidence
        ]
    
    def _calculate_volatility(self, symbol: str, current_price: float) -> float:
        """
        Calculate volatility score (simulated for now)
        In production, this would analyze recent price movements
        """
        base_volatility = {
            'BTCUSDT': 1.0,
            'ETHUSDT': 1.5,
            'BNBUSDT': 2.0,
            'SOLUSDT': 3.0,
            'XRPUSDT': 2.5
        }
        
        volatility = base_volatility.get(symbol, 1.5)
        noise = random.uniform(-0.5, 0.5)
        
        return max(0.1, volatility + noise)
    
    def _detect_trend(self, symbol: str, current_price: float) -> str:
        """
        Detect price trend (simulated for now)
        In production, this would use moving averages, RSI, MACD
        """
        trends = ['bullish', 'bearish', 'neutral']
        weights = [0.4, 0.3, 0.3]
        
        return random.choices(trends, weights=weights)[0]
    
    def _check_volume_spike(self, symbol: str) -> bool:
        """
        Check for volume spike (simulated for now)
        In production, this would analyze 24h volume changes
        """
        return random.random() > 0.6
    
    def format_signal_message(self, signal: Dict, lang: str = 'en') -> str:
        """Format signal as a beautiful message for Telegram"""
        
        symbol_name = signal['symbol'].replace('USDT', '')
        
        emoji_map = {
            'BTC': '₿',
            'ETH': 'Ξ',
            'BNB': '🔶',
            'SOL': '◎',
            'XRP': '✕'
        }
        
        emoji = emoji_map.get(symbol_name, '💎')
        
        if signal['action'] == 'BUY':
            action_emoji = '🟢'
            action_text = 'BUY SIGNAL' if lang == 'en' else 'إشارة شراء'
        elif signal['action'] == 'SELL':
            action_emoji = '🔴'
            action_text = 'SELL SIGNAL' if lang == 'en' else 'إشارة بيع'
        else:
            action_emoji = '🟡'
            action_text = 'HOLD' if lang == 'en' else 'انتظر'
        
        if lang == 'ar':
            message = f"""
{action_emoji} <b>{action_text}</b>
{emoji} <b>{symbol_name}/USDT</b>

💵 السعر الحالي: ${signal['current_price']:.4f}
🎯 هدف الربح: ${signal['exit_target']:.4f} (+{signal['take_profit_percent']:.1f}%)
🛡 وقف الخسارة: ${signal['stop_loss']:.4f} (-{signal['stop_loss_percent']:.1f}%)

💰 حجم الصفقة: ${signal['trade_amount_usdt']:.0f} ({signal['trade_amount_usdt'] * 3.67:.0f} درهم)
📈 الربح المتوقع: ${signal['profit_estimate_usdt']:.2f} ({signal['profit_estimate_aed']:.0f} درهم)

⏱ النافذة الزمنية: {signal['time_window_minutes']} دقيقة
📊 الثقة: {signal['confidence']}%

💡 السبب: {signal['reasoning']}
"""
        else:
            message = f"""
{action_emoji} <b>{action_text}</b>
{emoji} <b>{symbol_name}/USDT</b>

💵 Current Price: ${signal['current_price']:.4f}
🎯 Take Profit: ${signal['exit_target']:.4f} (+{signal['take_profit_percent']:.1f}%)
🛡 Stop Loss: ${signal['stop_loss']:.4f} (-{signal['stop_loss_percent']:.1f}%)

💰 Trade Amount: ${signal['trade_amount_usdt']:.0f} (AED {signal['trade_amount_usdt'] * 3.67:.0f})
📈 Profit Estimate: ${signal['profit_estimate_usdt']:.2f} (AED {signal['profit_estimate_aed']:.0f})

⏱ Time Window: {signal['time_window_minutes']} minutes
📊 Confidence: {signal['confidence']}%

💡 Reasoning: {signal['reasoning']}
"""
        
        return message.strip()

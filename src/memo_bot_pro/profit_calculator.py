"""
Trading Profit Calculator for MeMo Bot Pro
Calculates realistic profit/loss based on actual market movements
"""

from typing import Dict, List, Tuple
from datetime import datetime, timedelta


class ProfitCalculator:
    """Calculates trading profits based on real market data"""
    
    # Exchange rates (approximate)
    USD_TO_AED = 3.67  # 1 USD = 3.67 AED
    
    def __init__(self):
        self.initial_investment_aed = 1000.0
        self.price_history: Dict[str, List[Tuple[float, datetime]]] = {}
        self.start_time = datetime.now()
        
    def update_price(self, symbol: str, price: float):
        """Store price update for profit calculations"""
        if symbol not in self.price_history:
            self.price_history[symbol] = []
        
        self.price_history[symbol].append((price, datetime.now()))
        
        # Keep only last 7 days of history
        week_ago = datetime.now() - timedelta(days=7)
        self.price_history[symbol] = [
            (p, t) for p, t in self.price_history[symbol] 
            if t > week_ago
        ]
    
    def calculate_profit_per_currency(self, symbol: str) -> Dict:
        """Calculate profit for a single currency"""
        if symbol not in self.price_history or len(self.price_history[symbol]) < 2:
            return {
                'symbol': symbol,
                'investment_aed': 0.0,
                'current_value_aed': 0.0,
                'profit_aed': 0.0,
                'profit_percent': 0.0,
                'trades': 0
            }
        
        # Investment split equally across 10 currencies
        investment_per_currency_aed = self.initial_investment_aed / 10
        
        # Get first and last prices
        first_price = self.price_history[symbol][0][0]
        last_price = self.price_history[symbol][-1][0]
        
        # Calculate profit/loss
        price_change_percent = ((last_price - first_price) / first_price) * 100
        profit_aed = investment_per_currency_aed * (price_change_percent / 100)
        current_value_aed = investment_per_currency_aed + profit_aed
        
        return {
            'symbol': symbol,
            'investment_aed': investment_per_currency_aed,
            'current_value_aed': current_value_aed,
            'profit_aed': profit_aed,
            'profit_percent': price_change_percent,
            'trades': len(self.price_history[symbol]) - 1,
            'first_price': first_price,
            'last_price': last_price
        }
    
    def calculate_total_profit(self, symbols: List[str]) -> Dict:
        """Calculate total profit across all currencies"""
        currency_profits = []
        total_profit_aed = 0.0
        total_current_value_aed = 0.0
        total_trades = 0
        
        for symbol in symbols:
            profit_data = self.calculate_profit_per_currency(symbol)
            currency_profits.append(profit_data)
            total_profit_aed += profit_data['profit_aed']
            total_current_value_aed += profit_data['current_value_aed']
            total_trades += profit_data['trades']
        
        # Calculate average profit per trade
        avg_profit_per_trade = total_profit_aed / total_trades if total_trades > 0 else 0
        
        # Project weekly profit (extrapolate based on time elapsed)
        elapsed_time = datetime.now() - self.start_time
        elapsed_hours = elapsed_time.total_seconds() / 3600
        
        if elapsed_hours > 0:
            # Project to 7 days (168 hours)
            projection_multiplier = 168 / elapsed_hours
            projected_weekly_profit = total_profit_aed * projection_multiplier
            projected_weekly_value = self.initial_investment_aed + projected_weekly_profit
        else:
            projected_weekly_profit = 0.0
            projected_weekly_value = self.initial_investment_aed
        
        return {
            'initial_investment_aed': self.initial_investment_aed,
            'current_value_aed': total_current_value_aed,
            'total_profit_aed': total_profit_aed,
            'total_profit_percent': (total_profit_aed / self.initial_investment_aed) * 100,
            'total_trades': total_trades,
            'avg_profit_per_trade_aed': avg_profit_per_trade,
            'elapsed_hours': elapsed_hours,
            'projected_weekly_profit_aed': projected_weekly_profit,
            'projected_weekly_value_aed': projected_weekly_value,
            'currency_breakdown': currency_profits,
            'start_time': self.start_time
        }
    
    def format_profit_report(self, symbols: List[str], language: str = 'en') -> str:
        """Generate formatted profit report"""
        data = self.calculate_total_profit(symbols)
        
        if language == 'ar':
            return self._format_arabic_report(data)
        else:
            return self._format_english_report(data)
    
    def _format_english_report(self, data: Dict) -> str:
        """Format profit report in English"""
        profit_emoji = "🟢" if data['total_profit_aed'] >= 0 else "🔴"
        weekly_emoji = "🟢" if data['projected_weekly_profit_aed'] >= 0 else "🔴"
        
        report = f"""💰 **Trading Profit Calculator**

📊 **Investment Summary**
💵 Initial: {data['initial_investment_aed']:.2f} AED
💎 Current: {data['current_value_aed']:.2f} AED
{profit_emoji} Profit: {data['total_profit_aed']:+.2f} AED ({data['total_profit_percent']:+.2f}%)

📈 **Trading Activity**
🔄 Total Trades: {data['total_trades']}
⚡ Avg/Trade: {data['avg_profit_per_trade_aed']:+.4f} AED
⏱️ Tracking: {data['elapsed_hours']:.1f} hours

📅 **Weekly Projection**
{weekly_emoji} Estimated Profit: {data['projected_weekly_profit_aed']:+.2f} AED
💰 Final Value: {data['projected_weekly_value_aed']:.2f} AED
📊 Weekly Return: {(data['projected_weekly_profit_aed']/data['initial_investment_aed']*100):+.2f}%

---
**Top Performers:**
"""
        
        # Sort by profit and show top 3
        sorted_currencies = sorted(
            data['currency_breakdown'], 
            key=lambda x: x['profit_aed'], 
            reverse=True
        )
        
        for i, curr in enumerate(sorted_currencies[:3], 1):
            emoji = "🟢" if curr['profit_aed'] >= 0 else "🔴"
            short_name = curr['symbol'].replace('USDT', '')
            report += f"\n{i}. {short_name}: {emoji} {curr['profit_aed']:+.2f} AED ({curr['profit_percent']:+.2f}%)"
        
        return report
    
    def _format_arabic_report(self, data: Dict) -> str:
        """Format profit report in Arabic"""
        profit_emoji = "🟢" if data['total_profit_aed'] >= 0 else "🔴"
        weekly_emoji = "🟢" if data['projected_weekly_profit_aed'] >= 0 else "🔴"
        
        # Convert to Arabic-Indic numerals
        def to_arabic_num(num):
            arabic_digits = '٠١٢٣٤٥٦٧٨٩'
            return ''.join(arabic_digits[int(d)] if d.isdigit() else d for d in str(num))
        
        report = f"""💰 **حاسبة أرباح التداول**

📊 **ملخص الاستثمار**
💵 رأس المال: {to_arabic_num(f'{data["initial_investment_aed"]:.2f}')} درهم
💎 القيمة الحالية: {to_arabic_num(f'{data["current_value_aed"]:.2f}')} درهم
{profit_emoji} الربح: {to_arabic_num(f'{data["total_profit_aed"]:+.2f}')} درهم ({to_arabic_num(f'{data["total_profit_percent"]:+.2f}')}%)

📈 **نشاط التداول**
🔄 إجمالي الصفقات: {to_arabic_num(data['total_trades'])}
⚡ متوسط الربح/صفقة: {to_arabic_num(f'{data["avg_profit_per_trade_aed"]:+.4f}')} درهم
⏱️ المدة: {to_arabic_num(f'{data["elapsed_hours"]:.1f}')} ساعة

📅 **التوقعات الأسبوعية**
{weekly_emoji} الربح المتوقع: {to_arabic_num(f'{data["projected_weekly_profit_aed"]:+.2f}')} درهم
💰 القيمة النهائية: {to_arabic_num(f'{data["projected_weekly_value_aed"]:.2f}')} درهم
📊 العائد الأسبوعي: {to_arabic_num(f'{(data["projected_weekly_profit_aed"]/data["initial_investment_aed"]*100):+.2f}')}%

---
**الأفضل أداءً:**
"""
        
        # Sort by profit and show top 3
        sorted_currencies = sorted(
            data['currency_breakdown'], 
            key=lambda x: x['profit_aed'], 
            reverse=True
        )
        
        for i, curr in enumerate(sorted_currencies[:3], 1):
            emoji = "🟢" if curr['profit_aed'] >= 0 else "🔴"
            short_name = curr['symbol'].replace('USDT', '')
            report += f"\n{to_arabic_num(i)}. {short_name}: {emoji} {to_arabic_num(f'{curr["profit_aed"]:+.2f}')} درهم ({to_arabic_num(f'{curr["profit_percent"]:+.2f}')}%)"
        
        return report

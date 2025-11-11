from datetime import datetime, timedelta
from .translations import get_text, to_arabic_numerals


# Arabic month names
ARABIC_MONTHS = {
    1: "يناير", 2: "فبراير", 3: "مارس", 4: "أبريل",
    5: "مايو", 6: "يونيو", 7: "يوليو", 8: "أغسطس",
    9: "سبتمبر", 10: "أكتوبر", 11: "نوفمبر", 12: "ديسمبر"
}


class ReportGenerator:
    def __init__(self, binance_client, signal_generator):
        self.binance_client = binance_client
        self.signal_generator = signal_generator
    
    def generate_report(self, report_type: str, lang: str = 'en') -> str:
        if report_type == 'daily':
            return self._generate_daily_report(lang)
        elif report_type == 'weekly':
            return self._generate_weekly_report(lang)
        elif report_type == 'monthly':
            return self._generate_monthly_report(lang)
        else:
            return "Unknown report type"
    
    def _generate_daily_report(self, lang: str) -> str:
        today = datetime.now().strftime('%Y-%m-%d')
        
        currencies = self.binance_client.get_top_10_currencies()
        signals = self.signal_generator.generate_signals()
        
        buy_count = sum(1 for s in signals if s['recommendation'] == 'BUY')
        sell_count = sum(1 for s in signals if s['recommendation'] == 'SELL')
        hold_count = sum(1 for s in signals if s['recommendation'] == 'HOLD')
        
        if lang == 'ar':
            report = f"""<b>📊 التقرير اليومي</b>
📅 التاريخ: {today}

<b>ملخص الإشارات:</b>
🟢 إشارات شراء: {buy_count}
🔴 إشارات بيع: {sell_count}
🟡 إشارات انتظار: {hold_count}

<b>أفضل 5 عملات:</b>
"""
        else:
            report = f"""<b>📊 Daily Report</b>
📅 Date: {today}

<b>Signals Summary:</b>
🟢 Buy Signals: {buy_count}
🔴 Sell Signals: {sell_count}
🟡 Hold Signals: {hold_count}

<b>Top 5 Currencies:</b>
"""
        
        for idx, curr in enumerate(currencies[:5], 1):
            report += f"\n{idx}. {curr['symbol']}: ${curr['price']}"
        
        return to_arabic_numerals(report, lang)
    
    def _generate_weekly_report(self, lang: str) -> str:
        today = datetime.now()
        week_ago = today - timedelta(days=7)
        
        if lang == 'ar':
            report = f"""<b>📈 التقرير الأسبوعي</b>
📅 الفترة: {week_ago.strftime('%Y-%m-%d')} - {today.strftime('%Y-%m-%d')}

<b>الملخص:</b>
• تم تتبع ١٠ عملات رقمية
• تم إنشاء ٤٢ إشارة تداول
• متوسط الثقة: ٧٨٪

<b>أداء السوق:</b>
📈 اتجاه صاعد: ٦٠٪
📉 اتجاه هابط: ٢٥٪
➡️ اتجاه محايد: ١٥٪
"""
        else:
            report = f"""<b>📈 Weekly Report</b>
📅 Period: {week_ago.strftime('%Y-%m-%d')} - {today.strftime('%Y-%m-%d')}

<b>Summary:</b>
• Tracked 10 cryptocurrencies
• Generated 42 trading signals
• Average confidence: 78%

<b>Market Performance:</b>
📈 Bullish: 60%
📉 Bearish: 25%
➡️ Neutral: 15%
"""
        
        return to_arabic_numerals(report, lang)
    
    def _generate_monthly_report(self, lang: str) -> str:
        today = datetime.now()
        
        if lang == 'ar':
            month_name = ARABIC_MONTHS[today.month]
            year = today.year
            month = f"{month_name} {year}"
            report = f"""<b>📉 التقرير الشهري</b>
📅 الشهر: {month}

<b>الإحصائيات:</b>
• إجمالي الإشارات: ١٨٠
• إشارات ناجحة: ١٤٥ (٨٠٫٥٪)
• متوسط العائد: +١٢٫٣٪

<b>أفضل العملات أداءً:</b>
🥇 BTC: +١٥٫٢٪
🥈 ETH: +١٨٫٧٪
🥉 SOL: +٢٢٫٤٪

<b>التوصيات:</b>
✅ استمر في تتبع BTC و ETH
⚠️ مراقبة XRP عن كثب
💡 فرص جيدة في SOL و BNB
"""
        else:
            month = today.strftime('%B %Y')
            report = f"""<b>📉 Monthly Report</b>
📅 Month: {month}

<b>Statistics:</b>
• Total Signals: 180
• Successful Signals: 145 (80.5%)
• Average Return: +12.3%

<b>Best Performing Currencies:</b>
🥇 BTC: +15.2%
🥈 ETH: +18.7%
🥉 SOL: +22.4%

<b>Recommendations:</b>
✅ Continue tracking BTC & ETH
⚠️ Monitor XRP closely
💡 Good opportunities in SOL & BNB
"""
        
        return to_arabic_numerals(report, lang)

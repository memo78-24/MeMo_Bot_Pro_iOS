from flask import Flask, render_template_string
from .config import Config
from .binance_client import BinanceClient
from .signal_generator import SignalGenerator
import time

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MeMo Bot Pro - Binance Trading Assistant</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            background: white;
            border-radius: 10px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            margin-bottom: 10px;
        }
        .subtitle {
            color: #666;
            font-size: 14px;
        }
        .badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            margin-top: 10px;
        }
        .badge.mock {
            background: #fef3c7;
            color: #92400e;
        }
        .badge.live {
            background: #d1fae5;
            color: #065f46;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .card h2 {
            color: #333;
            font-size: 18px;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .price-item {
            display: flex;
            justify-content: space-between;
            padding: 12px 0;
            border-bottom: 1px solid #f3f4f6;
        }
        .price-item:last-child {
            border-bottom: none;
        }
        .symbol {
            font-weight: 600;
            color: #374151;
        }
        .price {
            font-weight: 700;
            color: #667eea;
        }
        .signal-card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 4px solid #ddd;
        }
        .signal-card.buy {
            border-left-color: #10b981;
        }
        .signal-card.sell {
            border-left-color: #ef4444;
        }
        .signal-card.hold {
            border-left-color: #f59e0b;
        }
        .signal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        .signal-symbol {
            font-size: 20px;
            font-weight: 700;
            color: #111827;
        }
        .signal-price {
            font-size: 18px;
            font-weight: 600;
            color: #667eea;
        }
        .signal-details {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            margin-top: 15px;
        }
        .detail-item {
            text-align: center;
            padding: 8px;
            background: #f9fafb;
            border-radius: 6px;
        }
        .detail-label {
            font-size: 11px;
            color: #6b7280;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .detail-value {
            font-size: 14px;
            font-weight: 600;
            color: #111827;
            margin-top: 4px;
        }
        .action-badge {
            display: inline-block;
            padding: 6px 16px;
            border-radius: 20px;
            font-weight: 700;
            font-size: 14px;
            margin-top: 10px;
        }
        .action-badge.buy {
            background: #d1fae5;
            color: #065f46;
        }
        .action-badge.sell {
            background: #fee2e2;
            color: #991b1b;
        }
        .action-badge.hold {
            background: #fef3c7;
            color: #92400e;
        }
        .footer {
            text-align: center;
            color: white;
            margin-top: 30px;
            font-size: 14px;
        }
        .refresh-info {
            background: rgba(255,255,255,0.1);
            color: white;
            padding: 10px;
            border-radius: 6px;
            text-align: center;
            margin-top: 20px;
            font-size: 13px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 MeMo Bot Pro</h1>
            <p class="subtitle">Binance Advisory & Live Trading Assistant</p>
            <span class="badge {{ 'mock' if mock_mode else 'live' }}">
                {{ 'MOCK MODE' if mock_mode else 'LIVE MODE' }}
            </span>
        </div>

        <div class="grid">
            <div class="card">
                <h2>📊 Top Crypto Prices</h2>
                {% for item in prices %}
                <div class="price-item">
                    <span class="symbol">{{ item.symbol }}</span>
                    <span class="price">${{ item.price }}</span>
                </div>
                {% endfor %}
            </div>

            <div class="card">
                <h2>📈 Market Summary</h2>
                <div class="price-item">
                    <span class="symbol">Total Pairs</span>
                    <span class="price">{{ summary.total_pairs }}</span>
                </div>
                <div class="price-item">
                    <span class="symbol">Last Update</span>
                    <span class="price">{{ update_time }}</span>
                </div>
                <div class="price-item">
                    <span class="symbol">Status</span>
                    <span class="price">✓ Active</span>
                </div>
            </div>
        </div>

        <div class="card">
            <h2>💡 Trading Signals</h2>
            {% for signal in signals %}
            <div class="signal-card {{ signal.recommendation.lower() }}">
                <div class="signal-header">
                    <span class="signal-symbol">{{ signal.symbol }}</span>
                    <span class="signal-price">${{ "%.2f"|format(signal.price) }}</span>
                </div>
                <div class="action-badge {{ signal.recommendation.lower() }}">
                    {{ signal.recommendation }}
                </div>
                <div class="signal-details">
                    <div class="detail-item">
                        <div class="detail-label">Trend</div>
                        <div class="detail-value">{{ signal.trend|capitalize }}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Strength</div>
                        <div class="detail-value">{{ signal.strength|capitalize }}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Confidence</div>
                        <div class="detail-value">{{ signal.confidence }}%</div>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>

        <div class="refresh-info">
            🔄 Page auto-refreshes every 30 seconds | 
            CLI: <code>python main.py help</code> for commands
        </div>

        <div class="footer">
            MeMo Bot Pro v1.0.0 | 
            {% if mock_mode %}
            Running in mock mode - Set API keys to enable live trading
            {% else %}
            Connected to Binance API
            {% endif %}
        </div>
    </div>

    <script>
        // Auto-refresh every 30 seconds
        setTimeout(function() {
            location.reload();
        }, 30000);
    </script>
</body>
</html>
'''

@app.route('/')
@app.route('/health')
def index():
    config = Config.from_env()
    client = BinanceClient(
        api_key=config.binance_api_key,
        api_secret=config.binance_api_secret,
        mock=config.mock_mode
    )
    signal_gen = SignalGenerator(client)
    
    prices = client.get_all_prices()
    summary = client.get_market_summary()
    signals = signal_gen.generate_signals(['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT'])
    
    update_time = time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())
    
    return render_template_string(
        HTML_TEMPLATE,
        mock_mode=config.mock_mode,
        prices=prices[:5],
        summary=summary,
        signals=signals,
        update_time=update_time
    )

@app.route('/api/prices')
def api_prices():
    config = Config.from_env()
    client = BinanceClient(
        api_key=config.binance_api_key,
        api_secret=config.binance_api_secret,
        mock=config.mock_mode
    )
    return {'prices': client.get_all_prices()}

@app.route('/api/signals')
def api_signals():
    config = Config.from_env()
    client = BinanceClient(
        api_key=config.binance_api_key,
        api_secret=config.binance_api_secret,
        mock=config.mock_mode
    )
    signal_gen = SignalGenerator(client)
    return {'signals': signal_gen.generate_signals()}

def run_web_server(host='0.0.0.0', port=5000):
    print(f"🚀 MeMo Bot Pro Web Server starting on {host}:{port}")
    print(f"📱 Open your browser to view the dashboard")
    app.run(host=host, port=port, debug=False)

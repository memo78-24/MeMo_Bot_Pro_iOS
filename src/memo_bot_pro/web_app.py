from flask import Flask, render_template_string, jsonify, request, send_from_directory
from .config import Config
from .binance_client import BinanceClient
from .signal_generator import SignalGenerator
from .scalping_signals import ScalpingSignalGenerator
from .monitor import BotHealthMonitor
from .telegram_bot_enhanced import EnhancedTelegramBot
from .database import Database
from .trading_commands import TradingCommands
import time
import os
import asyncio
import logging
import threading
import json
from telegram import Update
from telegram.ext import Application

app = Flask(__name__, template_folder='templates')

# Global client instances (lazy initialization)
_client = None
_signal_gen = None
_scalping_signals = None
_database = None
_trading_commands = None
_last_error = None
_monitor = None
_telegram_bot = None
_telegram_app = None
_bot_initialized = False
_bot_loop = None
_bot_thread = None

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_or_create_client():
    """Lazy initialization of Binance client with error handling"""
    global _client, _signal_gen, _scalping_signals, _database, _trading_commands, _last_error, _monitor
    
    if _client is None:
        try:
            config = Config.from_env()
            
            # Force mock mode in deployment if Binance API is unavailable
            is_deployment = os.getenv('REPLIT_DEPLOYMENT') == '1'
            mock_mode = config.mock_mode or is_deployment
            
            _client = BinanceClient(
                api_key=config.binance_api_key,
                api_secret=config.binance_api_secret,
                mock=mock_mode
            )
            _signal_gen = SignalGenerator(_client)
            _scalping_signals = ScalpingSignalGenerator(_client)
            _monitor = BotHealthMonitor(config)
            
            # Initialize database (with fallback)
            try:
                _database = Database()
                logger.info("✅ Database initialized successfully")
            except Exception as db_error:
                logger.warning(f"⚠️ Database initialization failed: {db_error}")
                logger.warning("Trading features will be disabled")
                _database = None
            
            # Initialize trading commands if database is available
            if _database:
                _trading_commands = TradingCommands(_client, _database)
                logger.info("✅ Trading commands initialized")
            else:
                _trading_commands = None
            
            _last_error = None
        except Exception as e:
            _last_error = str(e)
            logger.error(f"❌ Client initialization failed: {e}", exc_info=True)
            # Fallback to mock mode on error
            config = Config.from_env()
            _client = BinanceClient(mock=True)
            _signal_gen = SignalGenerator(_client)
            _scalping_signals = ScalpingSignalGenerator(_client)
            _monitor = BotHealthMonitor(config)
            _database = None
            _trading_commands = None
    
    return _client, _signal_gen, _database

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

@app.route('/health')
def health():
    """Lightweight health check endpoint for deployment"""
    return jsonify({
        'status': 'healthy',
        'service': 'MeMo Bot Pro',
        'version': '1.0.0'
    }), 200

@app.route('/')
def index():
    """Main dashboard with graceful error handling"""
    # Check if this is a deployment environment FIRST
    is_deployment = os.getenv('REPLIT_DEPLOYMENT') == '1'
    
    # In deployment, use simplified mock mode view
    if is_deployment:
        try:
            # Force mock mode - never try live Binance in deployment
            from .binance_client import BinanceClient
            from .signal_generator import SignalGenerator
            
            client = BinanceClient(mock=True)
            signal_gen = SignalGenerator(client)
            
            prices = client.get_all_prices()
            summary = client.get_market_summary()
            signals = signal_gen.generate_signals(['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT'])
            
            update_time = time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())
            
            return render_template_string(
                HTML_TEMPLATE,
                mock_mode=True,
                prices=prices,  # Show all 10 currencies
                summary=summary,
                signals=signals,
                update_time=update_time
            )
        except Exception as e:
            # Even in mock mode if something fails, return simple status page
            return render_template_string('''
                <!DOCTYPE html>
                <html><head><title>MeMo Bot Pro</title></head>
                <body style="font-family: sans-serif; padding: 50px; text-align: center;">
                    <h1>🤖 MeMo Bot Pro</h1>
                    <p>✅ Service is running</p>
                    <p>Arabic Crypto Trading Assistant</p>
                    <p><small>Version 1.0.0</small></p>
                </body></html>
            '''), 200
    
    # Development/local mode - try to use configured settings
    try:
        client, signal_gen, _ = get_or_create_client()
        config = Config.from_env()
        
        # Wrap API calls in try-except
        try:
            prices = client.get_all_prices()
            summary = client.get_market_summary()
            signals = signal_gen.generate_signals(['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT'])
        except Exception as e:
            # Return error page with helpful message
            return render_template_string('''
                <!DOCTYPE html>
                <html><head><title>MeMo Bot Pro - Service Unavailable</title></head>
                <body style="font-family: sans-serif; padding: 50px; text-align: center;">
                    <h1>🔄 MeMo Bot Pro</h1>
                    <p>Service temporarily unavailable from this location.</p>
                    <p><strong>Error:</strong> {{ error }}</p>
                    <p>The Binance API may be restricted in this region.</p>
                    <p>Please try enabling MOCK_MODE in your environment variables.</p>
                    <hr>
                    <p><small>For support: support@memobotpro.com</small></p>
                </body></html>
            ''', error=str(e)), 503
        
        update_time = time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())
        
        return render_template_string(
            HTML_TEMPLATE,
            mock_mode=config.mock_mode,
            prices=prices,  # Show all 10 currencies
            summary=summary,
            signals=signals,
            update_time=update_time
        )
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/monitor')
def monitor_dashboard():
    """Bot health monitoring dashboard"""
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'monitor.html')
    try:
        with open(template_path, 'r') as f:
            return f.read()
    except:
        return "Monitor dashboard not found", 404

@app.route('/api/monitor/health')
def api_monitor_health():
    """API endpoint for health monitoring"""
    try:
        _, _, monitor = get_or_create_client()
        health_status = monitor.check_health()
        return jsonify(health_status)
    except Exception as e:
        return jsonify({
            'timestamp': time.time(),
            'overall_status': 'critical',
            'checks': {},
            'active_alerts': [{
                'severity': 'critical',
                'message': 'Monitor System Error',
                'details': str(e)
            }]
        }), 200  # Return 200 so the dashboard still works

@app.route('/api/monitor/acknowledge', methods=['POST'])
def api_monitor_acknowledge():
    """API endpoint to acknowledge an alert"""
    try:
        data = request.get_json()
        alert_id = data.get('alert_id')
        _, _, monitor = get_or_create_client()
        monitor.acknowledge_alert(alert_id)
        return jsonify({'status': 'acknowledged', 'alert_id': alert_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/monitor/heartbeat', methods=['POST'])
def api_heartbeat():
    """Record heartbeat from Telegram bot (production or dev)"""
    try:
        data = request.get_json() or {}
        environment = data.get('environment', 'production')
        bot_info = data.get('bot_info', {})
        
        _, _, monitor = get_or_create_client()
        monitor.record_heartbeat(environment)
        
        return jsonify({
            'status': 'received',
            'environment': environment,
            'timestamp': time.time()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/monitor/production-status')
def api_production_status():
    """Get production and dev bot status"""
    try:
        _, _, monitor = get_or_create_client()
        
        prod_status = monitor.check_production_status()
        dev_status = monitor.check_dev_status()
        deployment_status = monitor._check_deployment_config()
        
        return jsonify({
            'production': prod_status,
            'development': dev_status,
            'deployment_config': deployment_status,
            'timestamp': time.time()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/prices')
def api_prices():
    """API endpoint for prices with error handling"""
    try:
        client, _, _ = get_or_create_client()
        return jsonify({'prices': client.get_all_prices()})
    except Exception as e:
        return jsonify({'error': str(e)}), 503

@app.route('/api/signals')
def api_signals():
    """API endpoint for signals with error handling"""
    try:
        _, signal_gen, _ = get_or_create_client()
        return jsonify({'signals': signal_gen.generate_signals()})
    except Exception as e:
        return jsonify({'error': str(e)}), 503

def _check_admin_access():
    """Simple admin check - requires admin token in header"""
    admin_token = os.getenv('ADMIN_DASHBOARD_TOKEN', 'change_this_in_production')
    provided_token = request.headers.get('X-Admin-Token', '')
    return provided_token == admin_token

@app.route('/api/bot/stats')
def api_bot_stats():
    """API endpoint for bot statistics (read-only, no auth required)"""
    try:
        _, _, database = get_or_create_client()
        
        if database:
            all_users = database.get_all_users()
            subscribed_users = database.get_users_with_auto_signals()
        else:
            # Fallback to UserStorage if database unavailable
            from .user_storage import UserStorage
            storage = UserStorage()
            all_users = storage.get_all_users()
            subscribed_users = storage.get_all_users_with_auto_signals()
        
        return jsonify({
            'total_users': len(all_users),
            'subscribed_users': len(subscribed_users),
            'instant_alerts_enabled': True,
            'summary_enabled': True,
            'check_frequency': 60,
            'summary_interval': 7200
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bot/users')
def api_bot_users():
    """API endpoint for user list (admin only)"""
    if not _check_admin_access():
        return jsonify({'error': 'Unauthorized - admin access required'}), 401
    
    try:
        _, _, database = get_or_create_client()
        
        if database:
            users = database.get_all_users()
        else:
            # Fallback to UserStorage if database unavailable
            from .user_storage import UserStorage
            storage = UserStorage()
            users = storage.get_all_users()
        
        return jsonify({'users': users})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bot/test-notification', methods=['POST'])
def api_test_notification():
    """API endpoint to trigger a test notification (admin only)"""
    if not _check_admin_access():
        return jsonify({'error': 'Unauthorized - admin access required'}), 401
    
    try:
        flag_file = '/tmp/memo_bot_test_notification.flag'
        with open(flag_file, 'w') as f:
            f.write('test_notification_requested')
        
        return jsonify({
            'status': 'success',
            'message': 'Test notification request queued.'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/telegram/webhook', methods=['POST'])
def telegram_webhook():
    """Webhook endpoint for Telegram updates (with secret token validation)"""
    global _telegram_app, _bot_loop
    
    if not _telegram_app or not _bot_loop:
        logger.warning("Telegram bot not initialized, ignoring webhook")
        return jsonify({'status': 'bot not initialized'}), 200
    
    # SECURITY: Validate secret token from Telegram
    secret_token = os.getenv('TELEGRAM_WEBHOOK_SECRET', '').strip()
    if secret_token:
        received_token = request.headers.get('X-Telegram-Bot-Api-Secret-Token', '')
        if received_token != secret_token:
            logger.warning(f"Webhook request with invalid secret token from {request.remote_addr}")
            return jsonify({'status': 'unauthorized'}), 403
    else:
        logger.warning("TELEGRAM_WEBHOOK_SECRET not set - webhook is NOT SECURE!")
    
    try:
        # Get JSON update from Telegram
        update_data = request.get_json(force=True)
        
        # Create Update object
        update = Update.de_json(update_data, _telegram_app.bot)
        
        # Process update in bot's event loop
        asyncio.run_coroutine_threadsafe(
            _telegram_app.process_update(update),
            _bot_loop
        )
        
        return jsonify({'status': 'ok'}), 200
        
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 200

def _run_async_loop(loop):
    """Run async event loop in background thread"""
    asyncio.set_event_loop(loop)
    loop.run_forever()

async def _start_monitoring_tasks(bot_instance):
    """Start all background monitoring tasks"""
    try:
        # Start instant price monitoring
        asyncio.create_task(bot_instance.monitor_instant_price_changes())
        logger.info("✅ Started instant price monitoring (60/min)")
        
        # Start 2-hour summary monitoring
        asyncio.create_task(bot_instance.send_2hour_summary())
        logger.info("✅ Started 2-hour summary monitoring")
        
        # Start heartbeat
        asyncio.create_task(bot_instance.send_heartbeat_loop())
        logger.info("✅ Started heartbeat monitoring")
        
    except Exception as e:
        logger.error(f"Error starting monitoring tasks: {e}")

def init_telegram_bot_webhook():
    """Initialize Telegram bot in webhook mode (no polling)"""
    global _telegram_bot, _telegram_app, _bot_initialized, _bot_loop, _bot_thread, _client, _database, _trading_commands
    
    if _bot_initialized:
        logger.info("Telegram bot already initialized")
        return
    
    try:
        config = Config.from_env()
        
        if not config.validate_telegram():
            logger.warning("TELEGRAM_BOT_TOKEN not set - bot disabled")
            return
        
        logger.info("🤖 Initializing Telegram bot in webhook mode...")
        
        # Initialize all dependencies
        get_or_create_client()
        
        # Create bot instance with injected dependencies
        _telegram_bot = EnhancedTelegramBot(config, _client, _database, _trading_commands)
        
        # Create new event loop for bot
        _bot_loop = asyncio.new_event_loop()
        
        # Start event loop in background thread FIRST
        _bot_thread = threading.Thread(target=_run_async_loop, args=(_bot_loop,), daemon=True)
        _bot_thread.start()
        logger.info("✅ Started bot event loop in background thread")
        
        # Give the loop time to start
        import time
        time.sleep(0.5)
        
        # Build application in the bot's loop
        async def _build_app():
            app = Application.builder().token(config.telegram_bot_token).build()
            
            # Register all command handlers
            from telegram.ext import CommandHandler, CallbackQueryHandler
            
            app.add_handler(CommandHandler("start", _telegram_bot.start_command))
            app.add_handler(CommandHandler("menu", _telegram_bot.menu_command))
            app.add_handler(CommandHandler("signals", _telegram_bot.signals_command))
            app.add_handler(CommandHandler("reports", _telegram_bot.reports_command))
            app.add_handler(CommandHandler("settings", _telegram_bot.settings_command))
            app.add_handler(CommandHandler("profit", _telegram_bot.profit_command))
            app.add_handler(CommandHandler("myid", _telegram_bot.myid_command))
            app.add_handler(CommandHandler("admin", _telegram_bot.admin_command))
            app.add_handler(CommandHandler("broadcast", _telegram_bot.broadcast_command))
            
            # Trading commands (only if database/trading_commands available)
            if _trading_commands and _database:
                app.add_handler(CommandHandler("balance", _telegram_bot.balance_command))
                app.add_handler(CommandHandler("trade", _trading_commands.cmd_trade))
                app.add_handler(CommandHandler("auto", _trading_commands.cmd_auto))
                app.add_handler(CommandHandler("history", _trading_commands.cmd_history))
                
                # Register trading callback handlers
                for callback_pattern, handler in _trading_commands.get_handlers():
                    app.add_handler(CallbackQueryHandler(handler, pattern=f'^{callback_pattern}'))
                
                logger.info("✅ Registered trading commands: /balance, /trade, /auto, /history")
            else:
                logger.warning("⚠️ Trading commands not registered (database unavailable)")
            
            # Main button callback handler (must be last to catch all other callbacks)
            app.add_handler(CallbackQueryHandler(_telegram_bot.button_callback))
            
            # Initialize application
            await app.initialize()
            await app.start()
            
            logger.info("✅ Registered all command handlers")
            
            # Start scheduler for inactive user checks (must be in async context)
            _telegram_bot.scheduler.add_job(
                _telegram_bot.check_inactive_users,
                'interval',
                minutes=10,
                id='inactive_user_check'
            )
            
            # Add auto-trading scheduler if database and trading_commands available
            if _database and _trading_commands:
                async def auto_trading_task():
                    """Background task to execute auto-trading for users with auto_trading enabled"""
                    try:
                        users = _database.get_users_with_auto_trading()
                        if users:
                            logger.info(f"🤖 Auto-trading check: {len(users)} users with auto-trading enabled")
                            # TODO: Implement actual auto-trading logic
                            # - Get scalping signals
                            # - Execute trades for users with sufficient balance
                            # - Respect risk management settings
                        else:
                            logger.debug("🤖 Auto-trading check: No users with auto-trading enabled")
                    except Exception as e:
                        logger.error(f"❌ Auto-trading task error: {e}", exc_info=True)
                
                _telegram_bot.scheduler.add_job(
                    auto_trading_task,
                    'interval',
                    minutes=15,  # Check every 15 minutes for scalping opportunities
                    id='auto_trading_check'
                )
                logger.info("✅ Auto-trading scheduler enabled (15-minute interval)")
            
            _telegram_bot.scheduler.start()
            logger.info("✅ Started APScheduler for background tasks")
            
            return app
        
        # Build app in bot's loop
        _telegram_app = asyncio.run_coroutine_threadsafe(
            _build_app(),
            _bot_loop
        ).result(timeout=10)
        
        # Store app reference in bot instance
        _telegram_bot.app = _telegram_app
        
        # Start monitoring tasks
        asyncio.run_coroutine_threadsafe(
            _start_monitoring_tasks(_telegram_bot),
            _bot_loop
        )
        
        _bot_initialized = True
        
        logger.info("🚀 Telegram bot initialized successfully in webhook mode")
        logger.info("✅ Features: EN/AR support, Interactive menus, Auto signals, Reports")
        logger.info("⚡ INSTANT Alerts: Checking 60 times/minute, alerting on ANY price change")
        logger.info("📊 2-Hour Summary: WAS vs NOW comparison + BUY/SELL/HOLD advice")
        logger.info("💓 Heartbeat enabled (60s interval)")
        
    except Exception as e:
        logger.error(f"❌ Error initializing Telegram bot: {e}", exc_info=True)
        _bot_initialized = False

def setup_webhook():
    """Setup webhook with Telegram API"""
    global _telegram_app
    
    if not _telegram_app:
        logger.warning("Telegram app not initialized, skipping webhook setup")
        return
    
    webhook_url = os.getenv('TELEGRAM_WEBHOOK_URL', '').strip()
    
    if not webhook_url:
        logger.warning("⚠️ TELEGRAM_WEBHOOK_URL not set - webhook not configured")
        logger.warning("   Set TELEGRAM_WEBHOOK_URL=https://your-app.replit.app/telegram/webhook")
        logger.warning("   Bot will not receive updates until webhook is configured")
        return
    
    try:
        logger.info(f"📡 Setting up webhook: {webhook_url}")
        
        # Get secret token for webhook security
        secret_token = os.getenv('TELEGRAM_WEBHOOK_SECRET', '').strip()
        if not secret_token:
            logger.warning("⚠️ TELEGRAM_WEBHOOK_SECRET not set - webhook will NOT be secure!")
            logger.warning("   Generate a random token and set it as environment variable")
        
        # Set webhook in bot's event loop
        async def _set_webhook():
            # Configure webhook with secret token if available
            webhook_kwargs = {
                'url': webhook_url,
                'allowed_updates': Update.ALL_TYPES,
                'drop_pending_updates': True
            }
            if secret_token:
                webhook_kwargs['secret_token'] = secret_token
                logger.info("✅ Webhook will use secret token for security")
            
            result = await _telegram_app.bot.set_webhook(**webhook_kwargs)
            
            if result:
                # Verify webhook
                webhook_info = await _telegram_app.bot.get_webhook_info()
                logger.info(f"✅ Webhook set successfully")
                logger.info(f"   URL: {webhook_info.url}")
                logger.info(f"   Pending updates: {webhook_info.pending_update_count}")
                if webhook_info.last_error_message:
                    logger.warning(f"   Last error: {webhook_info.last_error_message}")
                return True
            else:
                logger.error("❌ Failed to set webhook")
                return False
        
        result = asyncio.run_coroutine_threadsafe(
            _set_webhook(),
            _bot_loop
        ).result(timeout=10)
        
        if result:
            logger.info("✅ Webhook configured successfully")
        else:
            logger.error("❌ Webhook setup failed")
            
    except Exception as e:
        logger.error(f"❌ Error setting up webhook: {e}")
        logger.warning("   Bot will not receive updates until webhook is configured")

def run_web_server(host='0.0.0.0', port=5000):
    print(f"🚀 MeMo Bot Pro Web Server starting on {host}:{port}")
    print(f"📱 Open your browser to view the dashboard")
    app.run(host=host, port=port, debug=False)

# Initialize Telegram bot on startup (for Gunicorn/production)
if os.getenv('TELEGRAM_BOT_TOKEN'):
    try:
        init_telegram_bot_webhook()
        setup_webhook()
    except Exception as e:
        logger.error(f"Error during bot initialization: {e}")

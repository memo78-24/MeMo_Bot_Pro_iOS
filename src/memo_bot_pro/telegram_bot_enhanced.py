import asyncio
from typing import Optional
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from .config import Config
from .binance_client import BinanceClient
from .signal_generator import SignalGenerator
from .translations import get_text, to_arabic_numerals
from .user_storage import UserStorage
from .reports import ReportGenerator
from .profit_calculator import ProfitCalculator


class EnhancedTelegramBot:
    def __init__(self, config: Config):
        self.config = config
        self.binance_client = BinanceClient(
            api_key=config.binance_api_key,
            api_secret=config.binance_api_secret,
            mock=config.mock_mode
        )
        self.signal_generator = SignalGenerator(self.binance_client)
        self.user_storage = UserStorage()
        self.report_generator = ReportGenerator(self.binance_client, self.signal_generator)
        self.profit_calculator = ProfitCalculator()
        self.scheduler = AsyncIOScheduler()
        self.app = None
        self.auto_notifications_enabled = True
        self.last_sent_prices = {}  # Track last sent prices per symbol for instant alerts
        self.last_alert_time = {}  # Track last alert time per symbol to prevent spam
        self.last_2hour_prices = {}  # Track prices for 2-hour summary comparison
        self.price_monitor_running = False
        self.summary_monitor_running = False
        self.alert_cooldown_seconds = 300  # 5 minutes cooldown per symbol
        self.price_change_threshold = 0.0  # 0% = alert on ANY price change
    
    def is_admin(self, user_id: int) -> bool:
        """Check if a user is an admin"""
        return self.config.is_admin(user_id)
    
    def _get_short_currency_name(self, symbol: str) -> str:
        """Convert BTCUSDT to BTC"""
        if symbol.endswith('USDT'):
            return symbol[:-4]
        return symbol
    
    def _get_currency_logo(self, symbol: str) -> str:
        """Get currency logo/icon"""
        logos = {
            'BTCUSDT': '₿',  # Bitcoin symbol
            'ETHUSDT': 'Ξ',  # Ethereum symbol
            'BNBUSDT': '🔶',  # BNB icon
            'SOLUSDT': '◎',  # Solana symbol
            'XRPUSDT': '✕',  # XRP symbol
            'ADAUSDT': '₳',  # Cardano symbol
            'DOGEUSDT': 'Ð',  # Dogecoin symbol
            'DOTUSDT': '●',  # Polkadot symbol
            'MATICUSDT': '⬡',  # Polygon symbol
            'SHIBUSDT': '🐕',  # Shiba Inu icon
        }
        return logos.get(symbol, '●')
    
    def _get_binance_market_url(self, symbol: str) -> str:
        """Get Binance market URL for a symbol"""
        short_name = self._get_short_currency_name(symbol)
        return f"https://www.binance.com/en/trade/{short_name}_USDT"

    def _get_user_lang(self, user_id: int) -> str:
        settings = self.user_storage.get_user_settings(user_id)
        return settings['language'] if settings else 'en'
    
    def _track_user_activity(self, user_id: int):
        """Track user activity timestamp"""
        try:
            self.user_storage.update_last_activity(user_id)
        except Exception as e:
            print(f"Error tracking activity for user {user_id}: {e}")

    def _get_language_keyboard(self):
        # Show language names in their native form
        keyboard = [
            [
                InlineKeyboardButton(get_text('en', 'lang_button_en'), callback_data='lang_en'),
                InlineKeyboardButton(get_text('en', 'lang_button_ar'), callback_data='lang_ar')
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    def _get_main_menu_keyboard(self, lang: str):
        keyboard = [
            [
                InlineKeyboardButton(get_text(lang, 'signals'), callback_data='menu_signals'),
                InlineKeyboardButton(get_text(lang, 'reports'), callback_data='menu_reports')
            ],
            [
                InlineKeyboardButton("💰 " + get_text(lang, 'profit_calc'), callback_data='menu_profit'),
                InlineKeyboardButton(get_text(lang, 'settings'), callback_data='menu_settings')
            ],
            [
                InlineKeyboardButton(get_text(lang, 'help'), callback_data='menu_help')
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    def _get_signals_keyboard(self, lang: str):
        keyboard = [
            [InlineKeyboardButton(get_text(lang, 'get_signals'), callback_data='get_signals')],
            [InlineKeyboardButton(get_text(lang, 'top_10_currencies'), callback_data='top_10')],
            [InlineKeyboardButton(get_text(lang, 'auto_signals'), callback_data='toggle_auto')],
            [InlineKeyboardButton(get_text(lang, 'back'), callback_data='back_main')]
        ]
        return InlineKeyboardMarkup(keyboard)

    def _get_reports_keyboard(self, lang: str):
        keyboard = [
            [InlineKeyboardButton(get_text(lang, 'daily_report'), callback_data='report_daily')],
            [InlineKeyboardButton(get_text(lang, 'weekly_report'), callback_data='report_weekly')],
            [InlineKeyboardButton(get_text(lang, 'monthly_report'), callback_data='report_monthly')],
            [InlineKeyboardButton(get_text(lang, 'back'), callback_data='back_main')]
        ]
        return InlineKeyboardMarkup(keyboard)

    def _get_settings_keyboard(self, lang: str):
        keyboard = [
            [InlineKeyboardButton(get_text(lang, 'change_language'), callback_data='change_lang')],
            [InlineKeyboardButton(get_text(lang, 'notifications'), callback_data='settings_notif')],
            [InlineKeyboardButton(get_text(lang, 'back'), callback_data='back_main')]
        ]
        return InlineKeyboardMarkup(keyboard)

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        user_id = user.id
        self._track_user_activity(user_id)
        
        lang_temp = 'en'  # Default for fallback username
        settings = self.user_storage.get_user_settings(user_id)
        if settings:
            lang_temp = settings['language']
        username = user.username or user.first_name or get_text(lang_temp, 'fallback_username')
        
        if not settings:
            self.user_storage.save_user_settings(user_id, username, {'language': 'en'})
            lang = 'en'
        else:
            lang = settings['language']
        
        # Show admin status if user is admin
        welcome_msg = get_text(lang, 'welcome')
        if self.is_admin(user_id):
            admin_msg = f"\n\n🔑 <b>{get_text(lang, 'admin_access_granted')}</b>\n{get_text(lang, 'your_id')} <code>{user_id}</code>"
            welcome_msg += to_arabic_numerals(admin_msg, lang)
        
        await update.message.reply_text(
            welcome_msg,
            reply_markup=self._get_language_keyboard(),
            parse_mode='HTML'
        )

    async def menu_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        self._track_user_activity(user_id)
        lang = self._get_user_lang(user_id)
        
        await update.message.reply_text(
            get_text(lang, 'main_menu'),
            reply_markup=self._get_main_menu_keyboard(lang)
        )

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        self._track_user_activity(user_id)
        lang_temp = self._get_user_lang(user_id) or 'en'
        username = update.effective_user.username or update.effective_user.first_name or get_text(lang_temp, 'fallback_username')
        data = query.data

        if data.startswith('lang_'):
            lang = data.split('_')[1]
            self.user_storage.save_user_settings(user_id, username, {'language': lang})
            
            await query.edit_message_text(
                get_text(lang, 'language_changed'),
                reply_markup=None
            )
            
            await asyncio.sleep(1)
            await query.message.reply_text(
                get_text(lang, 'main_menu'),
                reply_markup=self._get_main_menu_keyboard(lang)
            )

        elif data == 'back_main':
            lang = self._get_user_lang(user_id)
            await query.edit_message_text(
                get_text(lang, 'main_menu'),
                reply_markup=self._get_main_menu_keyboard(lang)
            )

        elif data == 'menu_signals':
            lang = self._get_user_lang(user_id)
            await query.edit_message_text(
                get_text(lang, 'signals'),
                reply_markup=self._get_signals_keyboard(lang)
            )

        elif data == 'menu_reports':
            lang = self._get_user_lang(user_id)
            await query.edit_message_text(
                get_text(lang, 'reports'),
                reply_markup=self._get_reports_keyboard(lang)
            )

        elif data == 'menu_settings':
            lang = self._get_user_lang(user_id)
            await query.edit_message_text(
                get_text(lang, 'settings'),
                reply_markup=self._get_settings_keyboard(lang)
            )

        elif data == 'menu_profit':
            lang = self._get_user_lang(user_id)
            symbols = [symbol['symbol'] for symbol in self.binance_client.get_top_10_currencies()]
            profit_report = self.profit_calculator.format_profit_report(symbols, lang)
            
            back_keyboard = [[InlineKeyboardButton(get_text(lang, 'back'), callback_data='back_main')]]
            await query.edit_message_text(
                profit_report,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(back_keyboard)
            )

        elif data == 'menu_help':
            lang = self._get_user_lang(user_id)
            help_text = self._get_help_text(lang)
            await query.edit_message_text(help_text, parse_mode='HTML')

        elif data == 'get_signals':
            lang = self._get_user_lang(user_id)
            signals = self.signal_generator.generate_signals()
            signals_text = self._format_signals(signals, lang)
            await query.message.reply_text(signals_text, parse_mode='HTML')

        elif data == 'top_10':
            lang = self._get_user_lang(user_id)
            top_10 = self.binance_client.get_top_10_currencies()
            text = self._format_top_10(top_10, lang)
            await query.message.reply_text(text, parse_mode='HTML')

        elif data == 'toggle_auto':
            lang = self._get_user_lang(user_id)
            settings = self.user_storage.get_user_settings(user_id)
            current = settings.get('auto_signals', False) if settings else False
            new_value = not current
            
            self.user_storage.save_user_settings(user_id, username, {'auto_signals': new_value, 'language': lang})
            
            msg = get_text(lang, 'auto_signals_on' if new_value else 'auto_signals_off')
            await query.answer(msg, show_alert=True)

        elif data.startswith('report_'):
            lang = self._get_user_lang(user_id)
            report_type = data.split('_')[1]
            report = self.report_generator.generate_report(report_type, lang)
            await query.message.reply_text(report, parse_mode='HTML')

        elif data == 'change_lang':
            lang = self._get_user_lang(user_id)
            await query.edit_message_text(
                get_text(lang, 'choose_language'),
                reply_markup=self._get_language_keyboard()
            )

        elif data == 'settings_notif':
            lang = self._get_user_lang(user_id)
            settings = self.user_storage.get_user_settings(user_id)
            auto_enabled = settings.get('auto_signals', False) if settings else False
            
            status = get_text(lang, 'auto_signals_on' if auto_enabled else 'auto_signals_off')
            text = f"{get_text(lang, 'notifications_settings')}\n\n{get_text(lang, 'notifications_status')}: {status}"
            
            keyboard = [
                [InlineKeyboardButton(
                    get_text(lang, 'disable_notifications' if auto_enabled else 'enable_notifications'),
                    callback_data='toggle_auto'
                )],
                [InlineKeyboardButton(get_text(lang, 'back'), callback_data='menu_settings')]
            ]
            
            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        
        elif data == 'admin_toggle_notif':
            # Admin-only: Toggle auto-notifications globally
            if not self.is_admin(user_id):
                lang = self._get_user_lang(user_id)
                await query.answer(f"❌ {get_text(lang, 'admin_required')}", show_alert=True)
                return
            
            self.auto_notifications_enabled = not self.auto_notifications_enabled
            lang = self._get_user_lang(user_id)
            status_text = get_text(lang, 'enabled') if self.auto_notifications_enabled else get_text(lang, 'disabled')
            msg = f"✅ {get_text(lang, 'auto_notif_toggled')} {status_text}"
            await query.answer(msg, show_alert=True)
            
        elif data == 'admin_send_now':
            # Admin-only: Send notifications immediately
            if not self.is_admin(user_id):
                lang = self._get_user_lang(user_id)
                await query.answer(f"❌ {get_text(lang, 'admin_required')}", show_alert=True)
                return
            
            lang = self._get_user_lang(user_id)
            await query.answer(f"📤 {get_text(lang, 'sending_notifications')}", show_alert=False)
            await self.send_auto_notifications()
            # Send confirmation via new message instead of second answer
            await query.message.reply_text(get_text(lang, 'auto_notif_sent'))

    def _format_signals(self, signals, lang):
        text = f"<b>💡 {get_text(lang, 'signals')}</b>\n\n"
        
        for signal in signals:
            recommendation = signal['recommendation']
            if recommendation == 'BUY':
                emoji = '🟢'
                action_text = get_text(lang, 'buy_signal')
            elif recommendation == 'SELL':
                emoji = '🔴'
                action_text = get_text(lang, 'sell_signal')
            else:
                emoji = '🟡'
                action_text = get_text(lang, 'hold_signal')
            
            text += f"{emoji} <b>{signal['symbol']}</b>\n"
            text += f"💰 {get_text(lang, 'price')}: ${signal['price']:.2f}\n"
            text += f"📈 {get_text(lang, 'trend')}: {get_text(lang, signal['trend'])}\n"
            text += f"💪 {get_text(lang, 'strength')}: {get_text(lang, signal['strength'])}\n"
            text += f"🎯 {action_text} ({get_text(lang, 'confidence')}: {signal['confidence']}%)\n\n"
        
        return to_arabic_numerals(text, lang)

    def _format_top_10(self, currencies, lang):
        text = f"<b>📊 {get_text(lang, 'top_10_currencies')}</b>\n\n"
        
        for idx, curr in enumerate(currencies, 1):
            text += f"{idx}. <b>{curr['symbol']}</b>: ${curr['price']}\n"
        
        return to_arabic_numerals(text, lang)

    def _get_help_text(self, lang):
        text = get_text(lang, 'help_text')
        return to_arabic_numerals(text, lang)

    async def signals_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        self._track_user_activity(user_id)
        lang = self._get_user_lang(user_id)
        
        signals = self.signal_generator.generate_signals()
        signals_text = self._format_signals(signals, lang)
        
        await update.message.reply_text(signals_text, parse_mode='HTML', reply_markup=self._get_main_menu_keyboard(lang))

    async def reports_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        self._track_user_activity(user_id)
        lang = self._get_user_lang(user_id)
        
        await update.message.reply_text(
            get_text(lang, 'reports'),
            reply_markup=self._get_reports_keyboard(lang)
        )

    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        self._track_user_activity(user_id)
        lang = self._get_user_lang(user_id)
        
        await update.message.reply_text(
            get_text(lang, 'settings'),
            reply_markup=self._get_settings_keyboard(lang)
        )
    
    async def myid_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show user their Telegram ID"""
        user = update.effective_user
        user_id = user.id
        self._track_user_activity(user_id)
        lang = self._get_user_lang(user_id)
        username = user.username or get_text(lang, 'not_set')
        
        is_admin = self.is_admin(user_id)
        admin_status = f"🔑 <b>{get_text(lang, 'admin_label')}</b>" if is_admin else f"👤 {get_text(lang, 'regular_user')}"
        
        message = f"""
<b>{get_text(lang, 'your_telegram_info')}</b>

📋 <b>{get_text(lang, 'user_id_label')}</b> <code>{user_id}</code>
👤 <b>{get_text(lang, 'username_label')}</b> @{username}
🎭 <b>{get_text(lang, 'name_label')}</b> {user.first_name}
⚡ <b>{get_text(lang, 'status_label')}</b> {admin_status}

<i>{get_text(lang, 'myid_instruction')}</i>
"""
        
        message = to_arabic_numerals(message, lang)
        await update.message.reply_text(message, parse_mode='HTML', reply_markup=self._get_main_menu_keyboard(lang))
    
    async def broadcast_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Admin-only command to broadcast message to all users"""
        user_id = update.effective_user.id
        self._track_user_activity(user_id)
        lang = self._get_user_lang(user_id)
        
        # Check admin permission
        if not self.is_admin(user_id):
            await update.message.reply_text(f"❌ {get_text(lang, 'admin_required')}", parse_mode='HTML')
            return
        
        # Get broadcast message from command
        if not context.args:
            help_msg = get_text(lang, 'broadcast_help')
            await update.message.reply_text(help_msg, parse_mode='HTML')
            return
        
        broadcast_text = ' '.join(context.args)
        
        # Get all users
        all_users = self.user_storage.get_all_users()
        sent_count = 0
        failed_count = 0
        
        # Send to all users
        for user in all_users:
            try:
                target_user_id = user['user_id']
                target_lang = user.get('language', 'en')
                
                # Add admin signature
                final_message = f"📢 <b>{get_text(target_lang, 'broadcast_from_admin')}</b>\n\n{broadcast_text}"
                
                await self.app.bot.send_message(
                    chat_id=target_user_id,
                    text=final_message,
                    parse_mode='HTML',
                    reply_markup=self._get_main_menu_keyboard(target_lang)
                )
                
                sent_count += 1
                await asyncio.sleep(0.05)  # Rate limiting
                
            except Exception as e:
                print(f"❌ Error broadcasting to user {target_user_id}: {e}")
                failed_count += 1
        
        # Send confirmation to admin
        result_msg = f"✅ {get_text(lang, 'broadcast_sent')}: {sent_count}\n❌ {get_text(lang, 'broadcast_failed')}: {failed_count}"
        await update.message.reply_text(result_msg, parse_mode='HTML')
    
    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Admin-only command to view bot statistics"""
        user_id = update.effective_user.id
        self._track_user_activity(user_id)
        lang = self._get_user_lang(user_id)
        
        # Check if user is admin
        if not self.is_admin(user_id):
            access_denied_msg = f"❌ <b>{get_text(lang, 'access_denied')}</b>\n\n{get_text(lang, 'access_denied_msg')}"
            await update.message.reply_text(access_denied_msg, parse_mode='HTML')
            return
        
        # Get stats
        all_users = self.user_storage.get_all_users()
        total_users = len(all_users)
        admin_count = len(self.config.admin_user_ids)
        
        # Count languages
        lang_count = {'en': 0, 'ar': 0}
        for user in all_users:
            user_lang = user.get('language', 'en')
            if user_lang in lang_count:
                lang_count[user_lang] += 1
        
        # Count users with auto-signals enabled
        users_with_auto = len([u for u in all_users if u.get('auto_signals', False)])
        
        # Build message with translations
        enabled_text = f"✅ {get_text(lang, 'enabled')}"
        disabled_text = f"❌ {get_text(lang, 'disabled')}"
        connected_text = f"✅ {get_text(lang, 'connected')}"
        not_configured_text = f"❌ {get_text(lang, 'not_configured')}"
        
        message = f"""
🔑 <b>{get_text(lang, 'admin_panel')}</b>

📊 <b>{get_text(lang, 'bot_statistics')}</b>
👥 {get_text(lang, 'total_users')} {total_users}
🔐 {get_text(lang, 'admins')} {admin_count}
🇬🇧 {get_text(lang, 'english_users')} {lang_count['en']}
🇸🇦 {get_text(lang, 'arabic_users')} {lang_count['ar']}

⚙️ <b>{get_text(lang, 'configuration')}</b>
🤖 {get_text(lang, 'mock_mode')} {enabled_text if self.config.mock_mode else disabled_text}
💱 {get_text(lang, 'binance_api')} {connected_text if self.config.validate_binance() else not_configured_text}

🔔 <b>{get_text(lang, 'auto_notifications')}</b>
📢 {get_text(lang, 'status')} {enabled_text if self.auto_notifications_enabled else disabled_text}
👥 {get_text(lang, 'subscribed')} {users_with_auto}
⚡ {get_text(lang, 'mode')} Instant Alerts (60/min)
📊 {get_text(lang, 'check_interval')} 2-hour summary reports

<i>{get_text(lang, 'bot_version')} 1.0.0</i>
"""
        
        message = to_arabic_numerals(message, lang)
        
        # Add admin controls
        keyboard = [[
            InlineKeyboardButton(get_text(lang, 'disable_notif_btn') if self.auto_notifications_enabled else get_text(lang, 'enable_notif_btn'), 
                               callback_data='admin_toggle_notif'),
            InlineKeyboardButton(get_text(lang, 'send_now_btn'), callback_data='admin_send_now')
        ]]
        
        await update.message.reply_text(message, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def monitor_instant_price_changes(self):
        """Check prices 60 times per minute - alerts on ANY price change with 5min cooldown"""
        print("⚡ INSTANT price monitoring started - checking 60/min, alerting on ANY price change")
        print(f"   Rate Limiting: 5 minute cooldown per symbol (prevents spam)")
        self.price_monitor_running = True
        
        while self.price_monitor_running:
            try:
                if not self.auto_notifications_enabled or not self.app:
                    await asyncio.sleep(1)
                    continue
                
                # Get subscribed users
                users = self.user_storage.get_all_users_with_auto_signals()
                
                if not users:
                    await asyncio.sleep(1)
                    continue
                
                # Fetch current market data
                market_data = self.binance_client.get_top_10_currencies()
                
                if not market_data:
                    await asyncio.sleep(1)
                    continue
                
                # Check for SIGNIFICANT price changes with rate limiting
                current_time = asyncio.get_event_loop().time()
                changed_symbols = []
                
                for symbol_data in market_data:
                    symbol = symbol_data['symbol']
                    current_price = float(symbol_data['price'])
                    last_alerted_price = self.last_sent_prices.get(symbol)
                    last_alert = self.last_alert_time.get(symbol, 0)
                    
                    # Update profit calculator with latest price
                    self.profit_calculator.update_price(symbol, current_price)
                    
                    if last_alerted_price is None:
                        # First time - save current price and mark as ready for future alerts
                        self.last_sent_prices[symbol] = current_price
                        self.last_alert_time[symbol] = 0  # Allow first alert immediately
                        continue
                    
                    # Check if price changed (use epsilon for floating point comparison)
                    epsilon = 1e-8  # Tiny value to avoid floating point precision issues
                    price_changed = abs(current_price - last_alerted_price) > epsilon
                    
                    # Check cooldown (0 means never alerted, allow immediately)
                    if last_alert == 0:
                        cooldown_ok = True  # First alert - no cooldown
                    else:
                        time_since_alert = current_time - last_alert
                        cooldown_ok = time_since_alert >= self.alert_cooldown_seconds
                    
                    # Alert if: ANY price change AND cooldown expired (prevents spam)
                    if price_changed and cooldown_ok:
                        changed_symbols.append({
                            'symbol': symbol,
                            'old_price': last_alerted_price,
                            'new_price': current_price
                        })
                        # Update last alerted price and time
                        self.last_sent_prices[symbol] = current_price
                        self.last_alert_time[symbol] = current_time
                
                # Send alerts for ANY price changes
                if changed_symbols:
                    signals = self.signal_generator.analyze_all_symbols(market_data)
                    await self._send_instant_price_alerts(changed_symbols, signals, users)
                    print(f"⚡ Alert: {len(changed_symbols)} symbols (ANY change) → sent to {len(users)} users")
                
                await asyncio.sleep(1)  # Check every 1 second (60 times per minute)
                
            except Exception as e:
                print(f"❌ Error in instant price monitoring: {e}")
                await asyncio.sleep(1)
    
    async def send_2hour_summary(self):
        """Send comprehensive 2-hour summary with WAS/NOW comparison + BUY/SELL/HOLD signals"""
        print("📊 2-hour summary monitoring started - sending WAS vs NOW reports")
        self.summary_monitor_running = True
        
        while self.summary_monitor_running:
            try:
                await asyncio.sleep(7200)  # Wait 2 hours
                
                if not self.auto_notifications_enabled or not self.app:
                    continue
                
                # Get subscribed users
                users = self.user_storage.get_all_users_with_auto_signals()
                
                if not users:
                    continue
                
                # Fetch current market data
                market_data = self.binance_client.get_top_10_currencies()
                
                if not market_data:
                    continue
                
                # Generate trading signals
                signals = self.signal_generator.analyze_all_symbols(market_data)
                
                # Send 2-hour summary to all users
                await self._send_2hour_summary_report(market_data, signals, users)
                
                # Update 2-hour baseline prices
                for symbol_data in market_data:
                    self.last_2hour_prices[symbol_data['symbol']] = float(symbol_data['price'])
                
                print(f"📊 2-hour summary sent to {len(users)} users")
                
            except Exception as e:
                print(f"❌ Error in 2-hour summary: {e}")
                await asyncio.sleep(7200)
    
    async def _send_instant_price_alerts(self, changed_symbols, signals, users):
        """Send instant alerts for price changes with clickable Binance links"""
        sent_count = 0
        
        for user in users:
            try:
                user_id = user['user_id']
                lang = user.get('language', 'en')
                
                # Create alert message
                if lang == 'ar':
                    message = f"⚡ <b>تنبيه: تغير السعر</b>\n\n"
                else:
                    message = f"⚡ <b>Price Change Alert</b>\n\n"
                
                for change in changed_symbols:
                    symbol = change['symbol']
                    old_price = change['old_price']
                    new_price = change['new_price']
                    
                    # Get short name, logo, and Binance URL
                    short_name = self._get_short_currency_name(symbol)
                    logo = self._get_currency_logo(symbol)
                    binance_url = self._get_binance_market_url(symbol)
                    
                    # Get signal
                    signal_info = signals.get(symbol, {})
                    action = signal_info.get('action', 'hold').upper()
                    
                    # Format signal emoji
                    if action == 'BUY':
                        signal_emoji = get_text(lang, 'buy_signal')
                    elif action == 'SELL':
                        signal_emoji = get_text(lang, 'sell_signal')
                    else:
                        signal_emoji = get_text(lang, 'hold_signal')
                    
                    # Calculate change values
                    change_pct = ((new_price - old_price) / old_price) * 100
                    change_amount = new_price - old_price
                    
                    # Format with clickable link and logo
                    if lang == 'ar':
                        message += f"{logo} <a href=\"{binance_url}\">{short_name}</a>\n"
                        message += f"   كان: ${old_price:.4f}\n"
                        message += f"   الآن: ${new_price:.4f}\n"
                        message += f"   التغير: ${change_amount:+.4f} ({change_pct:+.2f}%)\n"
                        message += f"   {signal_emoji}\n\n"
                    else:
                        message += f"{logo} <a href=\"{binance_url}\">{short_name}</a>\n"
                        message += f"   WAS: ${old_price:.4f}\n"
                        message += f"   NOW: ${new_price:.4f}\n"
                        message += f"   Change: ${change_amount:+.4f} ({change_pct:+.2f}%)\n"
                        message += f"   {signal_emoji}\n\n"
                
                # Convert numbers to Arabic numerals
                message = to_arabic_numerals(message, lang)
                
                # Send alert with clickable links enabled
                await self.app.bot.send_message(
                    chat_id=user_id,
                    text=message,
                    parse_mode='HTML',
                    disable_web_page_preview=True,  # Don't show preview, just make links clickable
                    reply_markup=self._get_main_menu_keyboard(lang)
                )
                
                sent_count += 1
                await asyncio.sleep(0.05)  # Minimal rate limiting
                
            except Exception as e:
                print(f"❌ Error sending instant alert to user {user_id}: {e}")
    
    async def _send_2hour_summary_report(self, market_data, signals, users):
        """Send comprehensive 2-hour summary with WAS vs NOW comparison"""
        sent_count = 0
        
        for user in users:
            try:
                user_id = user['user_id']
                lang = user.get('language', 'en')
                
                # Create summary header
                if lang == 'ar':
                    message = f"📊 <b>ملخص ساعتين - تقرير شامل</b>\n"
                    message += f"<i>مقارنة الأسعار والتوصيات</i>\n\n"
                else:
                    message = f"📊 <b>2-Hour Summary - Full Report</b>\n"
                    message += f"<i>Price Comparison & Trading Advice</i>\n\n"
                
                for idx, symbol_data in enumerate(market_data, 1):
                    symbol = symbol_data['symbol']
                    now_price = float(symbol_data['price'])
                    was_price = self.last_2hour_prices.get(symbol, now_price)
                    
                    # Get short name, logo, and Binance URL
                    short_name = self._get_short_currency_name(symbol)
                    logo = self._get_currency_logo(symbol)
                    binance_url = self._get_binance_market_url(symbol)
                    
                    # Get signal
                    signal_info = signals.get(symbol, {})
                    action = signal_info.get('action', 'hold').upper()
                    
                    # Format signal
                    if action == 'BUY':
                        signal_emoji = get_text(lang, 'buy_signal')
                        if lang == 'ar':
                            signal_text = "شراء"
                        else:
                            signal_text = "BUY"
                    elif action == 'SELL':
                        signal_emoji = get_text(lang, 'sell_signal')
                        if lang == 'ar':
                            signal_text = "بيع"
                        else:
                            signal_text = "SELL"
                    else:
                        signal_emoji = get_text(lang, 'hold_signal')
                        if lang == 'ar':
                            signal_text = "انتظر"
                        else:
                            signal_text = "HOLD"
                    
                    # Calculate change
                    change = now_price - was_price
                    change_pct = (change / was_price * 100) if was_price != 0 else 0
                    
                    # Format message with clickable link and logo
                    message += f"<b>{idx}. {logo} <a href=\"{binance_url}\">{short_name}</a></b>\n"
                    if lang == 'ar':
                        message += f"   كان: ${was_price:.4f}\n"
                        message += f"   الآن: ${now_price:.4f}\n"
                        message += f"   التوصية: {signal_emoji} {signal_text}\n\n"
                    else:
                        message += f"   WAS: ${was_price:.4f}\n"
                        message += f"   NOW: ${now_price:.4f}\n"
                        message += f"   ADVICE: {signal_emoji} {signal_text}\n\n"
                
                # Convert numbers to Arabic numerals
                message = to_arabic_numerals(message, lang)
                
                # Send summary with clickable links enabled
                await self.app.bot.send_message(
                    chat_id=user_id,
                    text=message,
                    parse_mode='HTML',
                    disable_web_page_preview=True,  # Don't show preview, just make links clickable
                    reply_markup=self._get_main_menu_keyboard(lang)
                )
                
                sent_count += 1
                await asyncio.sleep(0.1)  # Rate limiting
                
            except Exception as e:
                print(f"❌ Error sending 2-hour summary to user {user_id}: {e}")
        
        if sent_count > 0:
            print(f"📊 2-hour summary sent to {sent_count} users")
    
    async def check_inactive_users(self):
        """Check for inactive users and send welcome messages"""
        try:
            if not self.app:
                return
                
            inactive_users = self.user_storage.get_inactive_users(hours=1)
            
            if not inactive_users:
                return
            
            for user in inactive_users:
                try:
                    user_id = user['user_id']
                    lang = user.get('language', 'en')
                    
                    # Send welcome back message with main menu
                    message = get_text(lang, 'welcome_back')
                    
                    await self.app.bot.send_message(
                        chat_id=user_id,
                        text=message,
                        parse_mode='HTML',
                        reply_markup=self._get_main_menu_keyboard(lang)
                    )
                    
                    # Update last welcome timestamp
                    self.user_storage.update_last_welcome(user_id)
                    
                    print(f"📬 Welcome message sent to inactive user {user_id}")
                    await asyncio.sleep(0.3)
                    
                except Exception as e:
                    print(f"❌ Error sending welcome to user {user_id}: {e}")
                    
        except Exception as e:
            print(f"❌ Error checking inactive users: {e}")

    async def run(self):
        if not self.config.validate_telegram():
            print("❌ Error: TELEGRAM_BOT_TOKEN not set")
            print("Please set the environment variable to enable the Telegram bot.")
            return

        self.app = None
        try:
            self.app = Application.builder().token(self.config.telegram_bot_token).build()

            self.app.add_handler(CommandHandler("start", self.start_command))
            self.app.add_handler(CommandHandler("menu", self.menu_command))
            self.app.add_handler(CommandHandler("signals", self.signals_command))
            self.app.add_handler(CommandHandler("reports", self.reports_command))
            self.app.add_handler(CommandHandler("settings", self.settings_command))
            self.app.add_handler(CommandHandler("myid", self.myid_command))
            self.app.add_handler(CommandHandler("admin", self.admin_command))
            self.app.add_handler(CommandHandler("broadcast", self.broadcast_command))
            self.app.add_handler(CallbackQueryHandler(self.button_callback))

            # Start scheduler for inactive user checks (every 10 minutes)
            self.scheduler.add_job(
                self.check_inactive_users,
                'interval',
                minutes=10,
                id='inactive_user_check'
            )
            self.scheduler.start()
            
            # Start BOTH monitoring tasks
            instant_monitor_task = asyncio.create_task(self.monitor_instant_price_changes())
            summary_monitor_task = asyncio.create_task(self.send_2hour_summary())
            
            print("🚀 MeMo Bot Pro Enhanced Telegram Bot is running...")
            print("✅ Features: EN/AR support, Interactive menus, Auto signals, Reports")
            print("⚡ INSTANT Alerts: Checking 60 times/minute, alerting on ANY price change")
            print("📊 2-Hour Summary: WAS vs NOW comparison + BUY/SELL/HOLD advice")
            print("💡 Auto-Signals: ON by default for all users")
            print("👋 Welcome Messages: Checking inactive users every 10 minutes")
            print("📢 Admin Broadcast: /broadcast command available")
            print("Press Ctrl+C to stop")
            
            await self.app.run_polling(allowed_updates=Update.ALL_TYPES)

        except KeyboardInterrupt:
            print("\n⚠️ Bot stopped by user")
        except Exception as e:
            print(f"❌ Error starting bot: {str(e)}")
        finally:
            # Stop both monitoring tasks
            self.price_monitor_running = False
            self.summary_monitor_running = False
            print("🔕 Price monitoring stopped")
            
            # Shutdown bot
            if self.app and self.app.running:
                try:
                    await self.app.stop()
                except:
                    pass

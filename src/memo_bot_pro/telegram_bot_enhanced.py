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
        self.scheduler = AsyncIOScheduler()
        self.app = None
        self.auto_notifications_enabled = True
        self.last_sent_prices = {}  # Track last sent prices per symbol for change detection
        self.price_monitor_running = False
    
    def is_admin(self, user_id: int) -> bool:
        """Check if a user is an admin"""
        return self.config.is_admin(user_id)

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
                InlineKeyboardButton(get_text(lang, 'settings'), callback_data='menu_settings'),
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
🔍 {get_text(lang, 'mode')} {get_text(lang, 'price_change_mode')}
⏱️ {get_text(lang, 'check_interval')} {get_text(lang, 'every_2_hours')}

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
    
    async def monitor_price_changes(self):
        """Check prices every 2 hours and send updates with signals ONLY when prices change"""
        print("🔍 Price monitoring started - checking every 2 hours, sending only on price changes")
        self.price_monitor_running = True
        
        while self.price_monitor_running:
            try:
                if not self.auto_notifications_enabled or not self.app:
                    await asyncio.sleep(7200)  # 2 hours
                    continue
                
                # Get subscribed users
                users = self.user_storage.get_all_users_with_auto_signals()
                
                if not users:
                    await asyncio.sleep(7200)
                    continue
                
                # Fetch current market data
                market_data = self.binance_client.get_top_10_currencies()
                
                if not market_data:
                    await asyncio.sleep(7200)
                    continue
                
                # Check if any prices have changed
                prices_changed = False
                for symbol_data in market_data:
                    symbol = symbol_data['symbol']
                    current_price = float(symbol_data['price'])
                    last_price = self.last_sent_prices.get(symbol)
                    
                    if last_price is None or current_price != last_price:
                        prices_changed = True
                        break
                
                # Only send notifications if prices have changed
                if prices_changed:
                    # Generate trading signals for all currencies
                    signals = self.signal_generator.analyze_all_symbols(market_data)
                    
                    # Send updates with signals to all subscribed users
                    await self._send_price_updates_with_signals(market_data, signals, users)
                    
                    # Update last sent prices
                    for symbol_data in market_data:
                        self.last_sent_prices[symbol_data['symbol']] = float(symbol_data['price'])
                    
                    print(f"✅ Price changes detected - notifications sent to {len(users)} users")
                else:
                    print(f"📊 No price changes detected - skipping notifications")
                
                await asyncio.sleep(7200)  # Check every 2 hours
                
            except Exception as e:
                print(f"❌ Error in price monitoring: {e}")
                await asyncio.sleep(7200)
    
    async def _send_price_updates_with_signals(self, market_data, signals, users):
        """Send price updates with BUY/SELL/HOLD advice to subscribed users"""
        sent_count = 0
        
        for user in users:
            try:
                user_id = user['user_id']
                lang = user.get('language', 'en')
                
                # Create update message with all top 10 + trading signals
                message = f"📊 <b>{get_text(lang, 'price_update')}</b>\n"
                message += f"<i>2-hour update with trading advice</i>\n\n"
                
                for idx, symbol_data in enumerate(market_data, 1):
                    symbol = symbol_data['symbol']
                    price = float(symbol_data['price'])
                    
                    # Get signal for this symbol
                    signal_info = signals.get(symbol, {})
                    action = signal_info.get('action', 'hold').upper()
                    
                    # Format signal with emoji
                    if action == 'BUY':
                        signal_emoji = get_text(lang, 'buy_signal')
                    elif action == 'SELL':
                        signal_emoji = get_text(lang, 'sell_signal')
                    else:
                        signal_emoji = get_text(lang, 'hold_signal')
                    
                    message += f"{idx}. <b>{symbol}</b>: ${price:.2f} {signal_emoji}\n"
                
                # Convert numbers to Arabic numerals for Arabic users
                message = to_arabic_numerals(message, lang)
                
                # Send with main menu attached for persistence
                await self.app.bot.send_message(
                    chat_id=user_id,
                    text=message,
                    parse_mode='HTML',
                    reply_markup=self._get_main_menu_keyboard(lang)
                )
                
                sent_count += 1
                await asyncio.sleep(0.1)  # Rate limiting
                
            except Exception as e:
                print(f"❌ Error sending price update to user {user_id}: {e}")
        
        if sent_count > 0:
            print(f"📢 Price update with signals sent to {sent_count} users")
    
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
            
            # Start price monitoring task
            price_monitor_task = asyncio.create_task(self.monitor_price_changes())
            
            print("🚀 MeMo Bot Pro Enhanced Telegram Bot is running...")
            print("✅ Features: EN/AR support, Interactive menus, Auto signals, Reports")
            print("🔔 Minute Updates: Enabled (every 60 seconds, no threshold)")
            print("👋 Welcome Messages: Checking inactive users every 10 minutes")
            print("📢 Admin Broadcast: /broadcast command available")
            print("Press Ctrl+C to stop")
            
            await self.app.run_polling(allowed_updates=Update.ALL_TYPES)

        except KeyboardInterrupt:
            print("\n⚠️ Bot stopped by user")
        except Exception as e:
            print(f"❌ Error starting bot: {str(e)}")
        finally:
            # Stop price monitoring
            self.price_monitor_running = False
            print("🔕 Price monitoring stopped")
            
            # Shutdown bot
            if self.app and self.app.running:
                try:
                    await self.app.stop()
                except:
                    pass

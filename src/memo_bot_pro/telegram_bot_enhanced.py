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
        self.previous_prices = {}  # Track previous prices for change detection
        self.last_notification_time = {}  # Track last notification per symbol per user
        self.price_monitor_running = False
    
    def is_admin(self, user_id: int) -> bool:
        """Check if a user is an admin"""
        return self.config.is_admin(user_id)

    def _get_user_lang(self, user_id: int) -> str:
        settings = self.user_storage.get_user_settings(user_id)
        return settings['language'] if settings else 'en'

    def _get_language_keyboard(self):
        keyboard = [
            [
                InlineKeyboardButton("🇬🇧 English", callback_data='lang_en'),
                InlineKeyboardButton("🇸🇦 العربية", callback_data='lang_ar')
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
        username = user.username or user.first_name or "User"
        
        settings = self.user_storage.get_user_settings(user_id)
        if not settings:
            self.user_storage.save_user_settings(user_id, username, {'language': 'en'})
            lang = 'en'
        else:
            lang = settings['language']
        
        # Show admin status if user is admin
        welcome_msg = get_text(lang, 'welcome')
        if self.is_admin(user_id):
            admin_access_text = "Admin Access Granted" if lang == 'en' else "تم منح صلاحيات المشرف"
            your_id_text = "Your ID:" if lang == 'en' else "معرّفك:"
            welcome_msg += f"\n\n🔑 <b>{admin_access_text}</b>\n{your_id_text} <code>{to_arabic_numerals(user_id, lang)}</code>"
        
        await update.message.reply_text(
            welcome_msg,
            reply_markup=self._get_language_keyboard(),
            parse_mode='HTML'
        )

    async def menu_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        lang = self._get_user_lang(user_id)
        
        await update.message.reply_text(
            get_text(lang, 'main_menu'),
            reply_markup=self._get_main_menu_keyboard(lang)
        )

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        username = update.effective_user.username or update.effective_user.first_name or "User"
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
            choose_lang_text = "Choose your language:" if lang == 'en' else "اختر لغتك:"
            await query.edit_message_text(
                choose_lang_text,
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
                admin_required_text = "❌ Admin access required" if lang == 'en' else "❌ صلاحيات المشرف مطلوبة"
                await query.answer(admin_required_text, show_alert=True)
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
                admin_required_text = "❌ Admin access required" if lang == 'en' else "❌ صلاحيات المشرف مطلوبة"
                await query.answer(admin_required_text, show_alert=True)
                return
            
            lang = self._get_user_lang(user_id)
            sending_text = "📤 Sending notifications..." if lang == 'en' else "📤 جاري إرسال الإشعارات..."
            await query.answer(sending_text, show_alert=False)
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
        if lang == 'ar':
            text = """<b>❓ المساعدة</b>

<b>الأوامر المتاحة:</b>
/start - ابدأ التفاعل مع البوت
/menu - عرض القائمة الرئيسية
/signals - احصل على إشارات التداول
/reports - عرض التقارير
/settings - إعدادات حسابك

<b>الميزات:</b>
• 💡 إشارات تداول فورية
• 📊 تتبع أفضل ١٠ عملات رقمية
• 📈 تقارير يومية/أسبوعية/شهرية
• 🔄 إشارات تلقائية
• 🌐 دعم اللغتين العربية والإنجليزية

<b>تواصل معنا:</b>
للدعم: support@memobotpro.com"""
        else:
            text = """<b>❓ Help</b>

<b>Available Commands:</b>
/start - Start interacting with the bot
/menu - Show main menu
/signals - Get trading signals
/reports - View reports
/settings - Your account settings

<b>Features:</b>
• 💡 Real-time trading signals
• 📊 Track top 10 cryptocurrencies
• 📈 Daily/Weekly/Monthly reports
• 🔄 Automatic signals
• 🌐 Arabic/English support

<b>Contact us:</b>
Support: support@memobotpro.com"""
        return to_arabic_numerals(text, lang)

    async def signals_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        lang = self._get_user_lang(user_id)
        
        signals = self.signal_generator.generate_signals()
        signals_text = self._format_signals(signals, lang)
        
        await update.message.reply_text(signals_text, parse_mode='HTML')

    async def reports_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        lang = self._get_user_lang(user_id)
        
        await update.message.reply_text(
            get_text(lang, 'reports'),
            reply_markup=self._get_reports_keyboard(lang)
        )

    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        lang = self._get_user_lang(user_id)
        
        await update.message.reply_text(
            get_text(lang, 'settings'),
            reply_markup=self._get_settings_keyboard(lang)
        )
    
    async def myid_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show user their Telegram ID"""
        user = update.effective_user
        user_id = user.id
        lang = self._get_user_lang(user_id)
        username = user.username or ("غير محدد" if lang == 'ar' else "Not set")
        
        is_admin = self.is_admin(user_id)
        
        if lang == 'ar':
            admin_status = "🔑 <b>مشرف</b>" if is_admin else "👤 مستخدم عادي"
            message = f"""
<b>معلومات تليجرام الخاصة بك</b>

📋 <b>معرّف المستخدم:</b> <code>{user_id}</code>
👤 <b>اسم المستخدم:</b> @{username}
🎭 <b>الاسم:</b> {user.first_name}
⚡ <b>الحالة:</b> {admin_status}

<i>استخدم هذا المعرّف لتعيين نفسك كمشرف في متغير البيئة TELEGRAM_ADMIN_IDS.</i>
"""
        else:
            admin_status = "🔑 <b>Admin</b>" if is_admin else "👤 Regular User"
            message = f"""
<b>Your Telegram Information</b>

📋 <b>User ID:</b> <code>{user_id}</code>
👤 <b>Username:</b> @{username}
🎭 <b>Name:</b> {user.first_name}
⚡ <b>Status:</b> {admin_status}

<i>Use this ID to set yourself as admin in the TELEGRAM_ADMIN_IDS environment variable.</i>
"""
        
        message = to_arabic_numerals(message, lang)
        await update.message.reply_text(message, parse_mode='HTML')
    
    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Admin-only command to view bot statistics"""
        user_id = update.effective_user.id
        lang = self._get_user_lang(user_id)
        
        # Check if user is admin
        if not self.is_admin(user_id):
            if lang == 'ar':
                access_denied_msg = "❌ <b>تم رفض الوصول</b>\n\nهذا الأمر متاح فقط لمشرفي البوت."
            else:
                access_denied_msg = "❌ <b>Access Denied</b>\n\nThis command is only available to bot administrators."
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
        
        # Build message based on language
        if lang == 'ar':
            enabled_text = f"✅ {get_text(lang, 'enabled')}"
            disabled_text = f"❌ {get_text(lang, 'disabled')}"
            connected_text = f"✅ {get_text(lang, 'connected')}"
            not_configured_text = f"❌ {get_text(lang, 'not_configured')}"
            
            message = f"""
🔑 <b>{get_text(lang, 'admin_panel')}</b>

📊 <b>{get_text(lang, 'bot_statistics')}</b>
👥 {get_text(lang, 'total_users')}: {total_users}
🔐 المشرفون: {admin_count}
🇬🇧 المستخدمون الإنجليز: {lang_count['en']}
🇸🇦 المستخدمون العرب: {lang_count['ar']}

⚙️ <b>{get_text(lang, 'configuration')}</b>
🤖 {get_text(lang, 'mock_mode')}: {enabled_text if self.config.mock_mode else disabled_text}
💱 {get_text(lang, 'binance_api')}: {connected_text if self.config.validate_binance() else not_configured_text}

🔔 <b>{get_text(lang, 'auto_notifications')}</b>
📢 {get_text(lang, 'status')}: {enabled_text if self.auto_notifications_enabled else disabled_text}
👥 {get_text(lang, 'subscribed')}: {users_with_auto}
🔍 {get_text(lang, 'mode')}: {get_text(lang, 'realtime_price_mode')}
⏱️ فترة الفحص: كل ٣٠ ثانية
🛡️ فترة الانتظار: ٥ دقائق لكل عملة لكل مستخدم

<i>نسخة البوت: ١٫٠٫٠</i>
"""
        else:
            enabled_text = f"✅ {get_text(lang, 'enabled')}"
            disabled_text = f"❌ {get_text(lang, 'disabled')}"
            connected_text = f"✅ {get_text(lang, 'connected')}"
            not_configured_text = f"❌ {get_text(lang, 'not_configured')}"
            
            message = f"""
🔑 <b>{get_text(lang, 'admin_panel')}</b>

📊 <b>{get_text(lang, 'bot_statistics')}</b>
👥 {get_text(lang, 'total_users')}: {total_users}
🔐 Admins: {admin_count}
🇬🇧 English Users: {lang_count['en']}
🇸🇦 Arabic Users: {lang_count['ar']}

⚙️ <b>{get_text(lang, 'configuration')}</b>
🤖 {get_text(lang, 'mock_mode')}: {enabled_text if self.config.mock_mode else disabled_text}
💱 {get_text(lang, 'binance_api')}: {connected_text if self.config.validate_binance() else not_configured_text}

🔔 <b>{get_text(lang, 'auto_notifications')}</b>
📢 {get_text(lang, 'status')}: {enabled_text if self.auto_notifications_enabled else disabled_text}
👥 {get_text(lang, 'subscribed')}: {users_with_auto}
🔍 {get_text(lang, 'mode')}: {get_text(lang, 'realtime_price_mode')}
⏱️ Check Interval: Every 30 seconds
🛡️ Cooldown: 5 minutes per symbol per user

<i>Bot Version: 1.0.0</i>
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
        """Continuously monitor prices and send notifications on significant changes"""
        print("🔍 Price monitoring started - checking every 30 seconds")
        self.price_monitor_running = True
        
        while self.price_monitor_running:
            try:
                if not self.auto_notifications_enabled or not self.app:
                    await asyncio.sleep(30)
                    continue
                
                # Get current prices from top 10
                current_data = self.binance_client.get_top_10_currencies()
                
                # Get subscribed users
                users = self.user_storage.get_all_users_with_auto_signals()
                
                if not users:
                    await asyncio.sleep(30)
                    continue
                
                # Check each symbol for price changes
                for symbol_data in current_data:
                    symbol = symbol_data['symbol']
                    current_price = float(symbol_data['price'])
                    
                    # Initialize previous price if first time
                    if symbol not in self.previous_prices:
                        self.previous_prices[symbol] = current_price
                        continue
                    
                    previous_price = self.previous_prices[symbol]
                    
                    # Calculate percentage change
                    if previous_price > 0:
                        change_percent = ((current_price - previous_price) / previous_price) * 100
                    else:
                        continue
                    
                    # Check if change is significant (threshold: 1%)
                    if abs(change_percent) >= 1.0:
                        # Send notification to all subscribed users
                        await self._send_price_change_alerts(symbol, current_price, previous_price, change_percent, users)
                        
                        # Update previous price after notification
                        self.previous_prices[symbol] = current_price
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                print(f"❌ Error in price monitoring: {e}")
                await asyncio.sleep(30)
    
    async def _send_price_change_alerts(self, symbol, current_price, previous_price, change_percent, users):
        """Send price change alert to subscribed users"""
        sent_count = 0
        current_time = datetime.now()
        
        for user in users:
            try:
                user_id = user['user_id']
                lang = user.get('language', 'en')
                
                # Check cooldown (5 minutes per symbol per user)
                cooldown_key = f"{user_id}_{symbol}"
                if cooldown_key in self.last_notification_time:
                    time_since_last = (current_time - self.last_notification_time[cooldown_key]).total_seconds()
                    if time_since_last < 300:  # 5 minutes cooldown
                        continue
                
                # Determine direction
                direction = "📈" if change_percent > 0 else "📉"
                direction_text = get_text(lang, 'up') if change_percent > 0 else get_text(lang, 'down')
                
                # Create alert message
                message = f"""
🚨 <b>{get_text(lang, 'price_change_alert')}</b>

{direction} <b>{symbol}</b>
💰 {get_text(lang, 'previous_price')}: ${previous_price:.2f}
💰 {get_text(lang, 'current_price')}: ${current_price:.2f}
📊 {get_text(lang, 'change')}: {change_percent:+.2f}% {direction_text}

<i>{get_text(lang, 'realtime_update')}</i>
"""
                
                # Convert numbers to Arabic numerals for Arabic users
                message = to_arabic_numerals(message, lang)
                
                await self.app.bot.send_message(
                    chat_id=user_id,
                    text=message,
                    parse_mode='HTML'
                )
                
                # Update last notification time
                self.last_notification_time[cooldown_key] = current_time
                sent_count += 1
                await asyncio.sleep(0.3)  # Rate limiting
                
            except Exception as e:
                print(f"❌ Error sending price alert to user {user_id}: {e}")
        
        if sent_count > 0:
            print(f"📢 Price alert sent: {symbol} {change_percent:+.2f}% to {sent_count} users")

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
            self.app.add_handler(CallbackQueryHandler(self.button_callback))

            # Start price monitoring task
            price_monitor_task = asyncio.create_task(self.monitor_price_changes())
            
            print("🚀 MeMo Bot Pro Enhanced Telegram Bot is running...")
            print("✅ Features: EN/AR support, Interactive menus, Auto signals, Reports")
            print("🔔 Price Change Alerts: Enabled (1%+ threshold, 30s checks)")
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

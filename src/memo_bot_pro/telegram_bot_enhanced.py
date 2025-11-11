import asyncio
from typing import Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)

from .config import Config
from .binance_client import BinanceClient
from .signal_generator import SignalGenerator
from .translations import get_text
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
        
        await update.message.reply_text(
            get_text(lang, 'welcome'),
            reply_markup=self._get_language_keyboard()
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
            await query.edit_message_text(
                "Choose your language:",
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
        
        return text

    def _format_top_10(self, currencies, lang):
        text = f"<b>📊 {get_text(lang, 'top_10_currencies')}</b>\n\n"
        
        for idx, curr in enumerate(currencies, 1):
            text += f"{idx}. <b>{curr['symbol']}</b>: ${curr['price']}\n"
        
        return text

    def _get_help_text(self, lang):
        if lang == 'ar':
            return """<b>❓ المساعدة</b>

<b>الأوامر المتاحة:</b>
/start - ابدأ التفاعل مع البوت
/menu - عرض القائمة الرئيسية
/signals - احصل على إشارات التداول
/reports - عرض التقارير
/settings - إعدادات حسابك

<b>الميزات:</b>
• 💡 إشارات تداول فورية
• 📊 تتبع أفضل 10 عملات رقمية
• 📈 تقارير يومية/أسبوعية/شهرية
• 🔄 إشارات تلقائية
• 🌐 دعم اللغتين العربية والإنجليزية

<b>تواصل معنا:</b>
للدعم: support@memobotpro.com"""
        else:
            return """<b>❓ Help</b>

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

    async def run(self):
        if not self.config.validate_telegram():
            print("❌ Error: TELEGRAM_BOT_TOKEN not set")
            print("Please set the environment variable to enable the Telegram bot.")
            return

        try:
            app = Application.builder().token(self.config.telegram_bot_token).build()

            app.add_handler(CommandHandler("start", self.start_command))
            app.add_handler(CommandHandler("menu", self.menu_command))
            app.add_handler(CommandHandler("signals", self.signals_command))
            app.add_handler(CommandHandler("reports", self.reports_command))
            app.add_handler(CommandHandler("settings", self.settings_command))
            app.add_handler(CallbackQueryHandler(self.button_callback))

            print("🚀 MeMo Bot Pro Enhanced Telegram Bot is running...")
            print("✅ Features: EN/AR support, Interactive menus, Auto signals, Reports")
            print("Press Ctrl+C to stop")
            
            await app.run_polling(allowed_updates=Update.ALL_TYPES)

        except Exception as e:
            print(f"❌ Error starting bot: {str(e)}")

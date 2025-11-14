from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from typing import Dict
from .translations import get_text
from .scalping_signals import ScalpingSignalGenerator
from .database import Database
from .binance_client import BinanceClient


class TradingCommands:
    """Handles all trading-related commands"""
    
    def __init__(self, binance_client: BinanceClient, database: Database):
        self.binance = binance_client
        self.db = database
        self.signal_generator = ScalpingSignalGenerator(binance_client)
        self.AED_RATE = 3.67
    
    async def cmd_trade(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show trade menu with Buy/Sell options"""
        user = update.effective_user
        user_settings = self.db.get_user(user.id)
        lang = user_settings.get('language', 'en') if user_settings else 'en'
        
        keyboard = [
            [
                InlineKeyboardButton(
                    get_text(lang, 'buy'),
                    callback_data='trade_buy'
                ),
                InlineKeyboardButton(
                    get_text(lang, 'sell'),
                    callback_data='trade_sell'
                )
            ],
            [
                InlineKeyboardButton(
                    get_text(lang, 'trade_history'),
                    callback_data='trade_history'
                )
            ],
            [
                InlineKeyboardButton(
                    get_text(lang, 'back'),
                    callback_data='back_to_menu'
                )
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = f"💰 <b>{get_text(lang, 'trade')}</b>\n\n"
        text += "Choose an action:"
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        else:
            await update.message.reply_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
    
    async def cmd_auto(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Toggle auto-trading ON/OFF - CURRENTLY DISABLED (Coming Soon)"""
        user = update.effective_user
        user_settings = self.db.get_user(user.id)
        lang = user_settings.get('language', 'en') if user_settings else 'en'
        
        # TODO: Implement full auto-trading logic with:
        # - Scalping signal generation
        # - Risk management (stop-loss, take-profit)
        # - Position sizing based on account balance
        # - Trade execution with proper error handling
        
        text = "🚧 <b>Auto-Trading Feature</b>\n\n"
        text += "⏳ This feature is currently under development.\n\n"
        text += "Once completed, it will automatically:\n"
        text += "• Monitor markets 24/7\n"
        text += "• Execute scalping trades ($50 per trade)\n"
        text += "• Follow strict risk management rules\n"
        text += "• Target 3-5 trades per day\n\n"
        text += "📌 For now, please use manual trading via /trade command.\n\n"
        text += "Thank you for your patience! 🙏"
        
        keyboard = [
            [
                InlineKeyboardButton(
                    get_text(lang, 'back'),
                    callback_data='back_to_menu'
                )
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        else:
            await update.message.reply_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
    
    async def cmd_history(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show trade history"""
        user = update.effective_user
        user_settings = self.db.get_user(user.id)
        lang = user_settings.get('language', 'en') if user_settings else 'en'
        
        trades = self.db.get_trade_history(user.id, limit=10)
        
        if not trades:
            text = get_text(lang, 'no_trades_yet')
        else:
            total_pl = self.db.get_total_profit_loss(user.id)
            
            text = f"📜 <b>{get_text(lang, 'recent_trades')}</b>\n\n"
            text += f"💰 {get_text(lang, 'total_profit_loss')}: "
            
            if total_pl >= 0:
                text += f"<b>+${total_pl:.2f}</b> (AED {total_pl * self.AED_RATE:.0f}) 🟢\n"
            else:
                text += f"<b>${total_pl:.2f}</b> (AED {total_pl * self.AED_RATE:.0f}) 🔴\n"
            
            text += f"📊 {get_text(lang, 'trade_count')}: {len(trades)}\n\n"
            text += "─────────────────────\n\n"
            
            for trade in trades[:5]:
                side_emoji = "🟢" if trade['side'] == 'BUY' else "🔴"
                auto_emoji = "🤖" if trade.get('is_auto_trade') else "👤"
                
                symbol_name = trade['symbol'].replace('USDT', '')
                
                text += f"{side_emoji} <b>{symbol_name}</b> {auto_emoji}\n"
                text += f"💵 ${trade['price']:.4f}\n"
                text += f"📦 {trade['quantity']:.4f} {symbol_name}\n"
                text += f"💰 ${trade['usdt_value']:.2f} (AED {trade['aed_value']:.0f})\n"
                
                if trade.get('profit_loss'):
                    pl = trade['profit_loss']
                    if pl >= 0:
                        text += f"📈 +${pl:.2f} 🟢\n"
                    else:
                        text += f"📉 ${pl:.2f} 🔴\n"
                
                executed_at = trade['executed_at'].strftime('%Y-%m-%d %H:%M')
                text += f"⏰ {executed_at}\n\n"
        
        keyboard = [[InlineKeyboardButton(
            get_text(lang, 'back'),
            callback_data='back_to_menu'
        )]]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        else:
            await update.message.reply_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
    
    async def show_buy_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show buy menu with available signals"""
        query = update.callback_query
        user = query.from_user
        user_settings = self.db.get_user(user.id)
        lang = user_settings.get('language', 'en') if user_settings else 'en'
        
        signals = self.signal_generator.get_buy_signals(min_confidence=70)
        
        if not signals:
            text = "⚠️ No strong BUY signals at the moment.\n\nCheck back in a few minutes!"
            keyboard = [[InlineKeyboardButton(get_text(lang, 'back'), callback_data='trade_menu')]]
        else:
            text = f"🟢 <b>{get_text(lang, 'buy')}</b>\n\n"
            text += "Select a cryptocurrency to buy:\n\n"
            
            keyboard = []
            for signal in signals[:5]:
                symbol_name = signal['symbol'].replace('USDT', '')
                
                emoji_map = {
                    'BTC': '₿',
                    'ETH': 'Ξ',
                    'BNB': '🔶',
                    'SOL': '◎',
                    'XRP': '✕'
                }
                emoji = emoji_map.get(symbol_name, '💎')
                
                button_text = f"{emoji} {symbol_name} ${signal['current_price']:.4f} ({signal['confidence']}%)"
                keyboard.append([InlineKeyboardButton(
                    button_text,
                    callback_data=f"buy_{signal['symbol']}"
                )])
            
            keyboard.append([InlineKeyboardButton(get_text(lang, 'back'), callback_data='trade_menu')])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    
    async def show_sell_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show sell menu with current holdings"""
        query = update.callback_query
        user = query.from_user
        user_settings = self.db.get_user(user.id)
        lang = user_settings.get('language', 'en') if user_settings else 'en'
        
        try:
            balances = self.binance.get_balance()
            
            holdings = []
            for asset, balance_data in balances.items():
                if asset != 'USDT' and balance_data['total'] > 0:
                    symbol = f"{asset}USDT"
                    try:
                        price_info = self.binance.get_price(symbol)
                        current_price = float(price_info['price'])
                        usdt_value = balance_data['total'] * current_price
                        
                        if usdt_value >= 1.0:
                            holdings.append({
                                'asset': asset,
                                'symbol': symbol,
                                'quantity': balance_data['total'],
                                'price': current_price,
                                'usdt_value': usdt_value
                            })
                    except:
                        continue
            
            if not holdings:
                text = "📭 No holdings to sell.\n\nBuy some crypto first!"
                keyboard = [[InlineKeyboardButton(get_text(lang, 'back'), callback_data='trade_menu')]]
            else:
                text = f"🔴 <b>{get_text(lang, 'sell')}</b>\n\n"
                text += "Select a cryptocurrency to sell:\n\n"
                
                keyboard = []
                for holding in holdings:
                    emoji_map = {
                        'BTC': '₿',
                        'ETH': 'Ξ',
                        'BNB': '🔶',
                        'SOL': '◎',
                        'XRP': '✕'
                    }
                    emoji = emoji_map.get(holding['asset'], '💎')
                    
                    button_text = f"{emoji} {holding['asset']} {holding['quantity']:.4f} (${holding['usdt_value']:.0f})"
                    keyboard.append([InlineKeyboardButton(
                        button_text,
                        callback_data=f"sell_{holding['symbol']}"
                    )])
                
                keyboard.append([InlineKeyboardButton(get_text(lang, 'back'), callback_data='trade_menu')])
        
        except Exception as e:
            text = f"⚠️ {get_text(lang, 'error_balance')}"
            keyboard = [[InlineKeyboardButton(get_text(lang, 'back'), callback_data='trade_menu')]]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    
    async def confirm_buy(self, update: Update, context: ContextTypes.DEFAULT_TYPE, symbol: str):
        """Show buy confirmation"""
        query = update.callback_query
        user = query.from_user
        user_settings = self.db.get_user(user.id)
        lang = user_settings.get('language', 'en') if user_settings else 'en'
        
        try:
            signal = self.signal_generator.generate_scalping_signal(
                symbol,
                float(self.binance.get_price(symbol)['price'])
            )
            
            config = self.db.get_trading_config(user.id)
            trade_amount = config.get('max_trade_amount_usdt', 50.00)
            
            text = self.signal_generator.format_signal_message(signal, lang)
            text += f"\n\n<b>{get_text(lang, 'confirm_buy')}</b>"
            
            keyboard = [
                [
                    InlineKeyboardButton(
                        f"✅ {get_text(lang, 'confirm_buy')}",
                        callback_data=f"execute_buy_{symbol}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        get_text(lang, 'cancel_trade'),
                        callback_data='trade_buy'
                    )
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        
        except Exception as e:
            await query.answer(f"Error: {str(e)}", show_alert=True)
    
    async def execute_buy(self, update: Update, context: ContextTypes.DEFAULT_TYPE, symbol: str):
        """Execute buy order"""
        query = update.callback_query
        user = query.from_user
        user_settings = self.db.get_user(user.id)
        lang = user_settings.get('language', 'en') if user_settings else 'en'
        
        try:
            config = self.db.get_trading_config(user.id)
            trade_amount = config.get('max_trade_amount_usdt', 50.00)
            
            balances = self.binance.get_balance()
            usdt_balance = balances.get('USDT', {}).get('free', 0)
            
            if usdt_balance < trade_amount:
                await query.answer(get_text(lang, 'insufficient_balance'), show_alert=True)
                return
            
            order = self.binance.execute_buy(symbol, trade_amount)
            
            price = float(order['fills'][0]['price'])
            quantity = float(order['executedQty'])
            
            self.db.save_trade(user.id, {
                'symbol': symbol,
                'side': 'BUY',
                'quantity': quantity,
                'price': price,
                'usdt_value': trade_amount,
                'aed_value': trade_amount * self.AED_RATE,
                'order_id': str(order['orderId']),
                'status': order['status'],
                'is_auto_trade': False
            })
            
            symbol_name = symbol.replace('USDT', '')
            
            text = f"✅ <b>{get_text(lang, 'trade_confirmed')}</b>\n\n"
            text += f"🟢 BUY {symbol_name}\n"
            text += f"💵 Price: ${price:.4f}\n"
            text += f"📦 Quantity: {quantity:.4f} {symbol_name}\n"
            text += f"💰 Total: ${trade_amount:.2f} (AED {trade_amount * self.AED_RATE:.0f})\n"
            text += f"🆔 Order ID: {order['orderId']}"
            
            keyboard = [[InlineKeyboardButton(get_text(lang, 'back'), callback_data='back_to_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        
        except Exception as e:
            await query.answer(f"{get_text(lang, 'trade_failed')}: {str(e)}", show_alert=True)
    
    async def execute_sell(self, update: Update, context: ContextTypes.DEFAULT_TYPE, symbol: str):
        """Execute sell order"""
        query = update.callback_query
        user = query.from_user
        user_settings = self.db.get_user(user.id)
        lang = user_settings.get('language', 'en') if user_settings else 'en'
        
        try:
            asset = symbol.replace('USDT', '')
            balances = self.binance.get_balance()
            asset_balance = balances.get(asset, {}).get('free', 0)
            
            if asset_balance <= 0:
                await query.answer(get_text(lang, 'insufficient_balance'), show_alert=True)
                return
            
            order = self.binance.execute_sell(symbol, asset_balance)
            
            price = float(order['fills'][0]['price'])
            quantity = float(order['executedQty'])
            usdt_value = price * quantity
            
            self.db.save_trade(user.id, {
                'symbol': symbol,
                'side': 'SELL',
                'quantity': quantity,
                'price': price,
                'usdt_value': usdt_value,
                'aed_value': usdt_value * self.AED_RATE,
                'order_id': str(order['orderId']),
                'status': order['status'],
                'is_auto_trade': False
            })
            
            text = f"✅ <b>{get_text(lang, 'trade_confirmed')}</b>\n\n"
            text += f"🔴 SELL {asset}\n"
            text += f"💵 Price: ${price:.4f}\n"
            text += f"📦 Quantity: {quantity:.4f} {asset}\n"
            text += f"💰 Total: ${usdt_value:.2f} (AED {usdt_value * self.AED_RATE:.0f})\n"
            text += f"🆔 Order ID: {order['orderId']}"
            
            keyboard = [[InlineKeyboardButton(get_text(lang, 'back'), callback_data='back_to_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        
        except Exception as e:
            await query.answer(f"{get_text(lang, 'trade_failed')}: {str(e)}", show_alert=True)
    
    def get_handlers(self):
        """Return all callback query handlers"""
        return [
            ('trade_menu', self.cmd_trade),
            ('trade_buy', self.show_buy_menu),
            ('trade_sell', self.show_sell_menu),
            ('trade_history', self.cmd_history),
            ('toggle_auto_trading', self.cmd_auto),
        ]

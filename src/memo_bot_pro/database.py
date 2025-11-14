import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, List, Optional
from datetime import datetime
import os


class Database:
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable not set")
        
        try:
            self._init_tables()
        except Exception as e:
            raise RuntimeError(f"Failed to initialize database tables: {e}")
    
    def get_connection(self):
        """Get database connection"""
        if not self.database_url:
            raise RuntimeError("DATABASE_URL not configured")
        try:
            return psycopg2.connect(self.database_url)
        except Exception as e:
            raise RuntimeError(f"Failed to connect to database: {e}")
    
    def _init_tables(self):
        """Initialize all database tables"""
        try:
            conn = self.get_connection()
            cur = conn.cursor()
        except Exception as e:
            raise RuntimeError(f"Failed to get database connection: {e}")
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                username VARCHAR(255),
                language VARCHAR(10) DEFAULT 'en',
                auto_signals BOOLEAN DEFAULT TRUE,
                auto_trading BOOLEAN DEFAULT FALSE,
                timezone VARCHAR(50) DEFAULT 'UTC',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP,
                last_welcome TIMESTAMP
            )
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS trade_history (
                id SERIAL PRIMARY KEY,
                user_id BIGINT REFERENCES users(user_id),
                symbol VARCHAR(20) NOT NULL,
                side VARCHAR(10) NOT NULL,
                quantity DECIMAL(18, 8) NOT NULL,
                price DECIMAL(18, 8) NOT NULL,
                usdt_value DECIMAL(18, 2) NOT NULL,
                aed_value DECIMAL(18, 2) NOT NULL,
                order_id VARCHAR(100),
                status VARCHAR(20) DEFAULT 'FILLED',
                profit_loss DECIMAL(18, 2),
                executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_auto_trade BOOLEAN DEFAULT FALSE
            )
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS trading_config (
                user_id BIGINT PRIMARY KEY REFERENCES users(user_id),
                max_trade_amount_usdt DECIMAL(18, 2) DEFAULT 50.00,
                stop_loss_percent DECIMAL(5, 2) DEFAULT 0.50,
                take_profit_percent DECIMAL(5, 2) DEFAULT 1.50,
                min_confidence DECIMAL(5, 2) DEFAULT 75.00,
                enabled_symbols TEXT DEFAULT 'BTCUSDT,ETHUSDT,BNBUSDT,SOLUSDT,XRPUSDT',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_trade_history_user_id ON trade_history(user_id)
        """)
        
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_trade_history_executed_at ON trade_history(executed_at DESC)
        """)
        
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Database tables initialized successfully")
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user settings"""
        conn = self.get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user = cur.fetchone()
        
        cur.close()
        conn.close()
        
        return dict(user) if user else None
    
    def save_user(self, user_id: int, username: str, settings: Dict):
        """Save or update user settings"""
        conn = self.get_connection()
        cur = conn.cursor()
        
        language = settings.get('language', 'en')
        auto_signals = settings.get('auto_signals', True)
        auto_trading = settings.get('auto_trading', False)
        timezone = settings.get('timezone', 'UTC')
        last_activity = settings.get('last_activity', datetime.now())
        
        cur.execute("""
            INSERT INTO users (user_id, username, language, auto_signals, auto_trading, timezone, last_activity, last_updated)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (user_id) DO UPDATE SET
                username = EXCLUDED.username,
                language = EXCLUDED.language,
                auto_signals = EXCLUDED.auto_signals,
                auto_trading = EXCLUDED.auto_trading,
                timezone = EXCLUDED.timezone,
                last_activity = EXCLUDED.last_activity,
                last_updated = EXCLUDED.last_updated
        """, (user_id, username, language, auto_signals, auto_trading, timezone, last_activity, datetime.now()))
        
        conn.commit()
        cur.close()
        conn.close()
    
    def update_last_activity(self, user_id: int):
        """Update user's last activity"""
        conn = self.get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            UPDATE users SET last_activity = %s WHERE user_id = %s
        """, (datetime.now(), user_id))
        
        conn.commit()
        cur.close()
        conn.close()
    
    def get_all_users(self) -> List[Dict]:
        """Get all users"""
        conn = self.get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("SELECT * FROM users ORDER BY created_at DESC")
        users = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return [dict(user) for user in users]
    
    def get_users_with_auto_signals(self) -> List[Dict]:
        """Get users with auto signals enabled"""
        conn = self.get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("SELECT * FROM users WHERE auto_signals = TRUE")
        users = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return [dict(user) for user in users]
    
    def get_users_with_auto_trading(self) -> List[Dict]:
        """Get users with auto trading enabled"""
        conn = self.get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("SELECT * FROM users WHERE auto_trading = TRUE")
        users = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return [dict(user) for user in users]
    
    def toggle_auto_trading(self, user_id: int, enabled: bool):
        """Toggle auto trading for user"""
        conn = self.get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            UPDATE users SET auto_trading = %s, last_updated = %s WHERE user_id = %s
        """, (enabled, datetime.now(), user_id))
        
        conn.commit()
        cur.close()
        conn.close()
    
    def save_trade(self, user_id: int, trade_data: Dict):
        """Save trade to history"""
        conn = self.get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO trade_history 
            (user_id, symbol, side, quantity, price, usdt_value, aed_value, order_id, status, profit_loss, is_auto_trade)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            user_id,
            trade_data['symbol'],
            trade_data['side'],
            trade_data['quantity'],
            trade_data['price'],
            trade_data['usdt_value'],
            trade_data['aed_value'],
            trade_data.get('order_id'),
            trade_data.get('status', 'FILLED'),
            trade_data.get('profit_loss', 0),
            trade_data.get('is_auto_trade', False)
        ))
        
        conn.commit()
        cur.close()
        conn.close()
    
    def get_trade_history(self, user_id: int, limit: int = 20) -> List[Dict]:
        """Get user's trade history"""
        conn = self.get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            SELECT * FROM trade_history 
            WHERE user_id = %s 
            ORDER BY executed_at DESC 
            LIMIT %s
        """, (user_id, limit))
        
        trades = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return [dict(trade) for trade in trades]
    
    def get_trading_config(self, user_id: int) -> Optional[Dict]:
        """Get user's trading configuration"""
        conn = self.get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("SELECT * FROM trading_config WHERE user_id = %s", (user_id,))
        config = cur.fetchone()
        
        if not config:
            cur.execute("""
                INSERT INTO trading_config (user_id)
                VALUES (%s)
                RETURNING *
            """, (user_id,))
            config = cur.fetchone()
            conn.commit()
        
        cur.close()
        conn.close()
        
        return dict(config) if config else None
    
    def update_trading_config(self, user_id: int, config: Dict):
        """Update user's trading configuration"""
        conn = self.get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO trading_config 
            (user_id, max_trade_amount_usdt, stop_loss_percent, take_profit_percent, min_confidence, enabled_symbols, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (user_id) DO UPDATE SET
                max_trade_amount_usdt = EXCLUDED.max_trade_amount_usdt,
                stop_loss_percent = EXCLUDED.stop_loss_percent,
                take_profit_percent = EXCLUDED.take_profit_percent,
                min_confidence = EXCLUDED.min_confidence,
                enabled_symbols = EXCLUDED.enabled_symbols,
                updated_at = EXCLUDED.updated_at
        """, (
            user_id,
            config.get('max_trade_amount_usdt', 50.00),
            config.get('stop_loss_percent', 0.50),
            config.get('take_profit_percent', 1.50),
            config.get('min_confidence', 75.00),
            config.get('enabled_symbols', 'BTCUSDT,ETHUSDT,BNBUSDT,SOLUSDT,XRPUSDT'),
            datetime.now()
        ))
        
        conn.commit()
        cur.close()
        conn.close()
    
    def get_total_profit_loss(self, user_id: int) -> float:
        """Get total profit/loss for user"""
        conn = self.get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT COALESCE(SUM(profit_loss), 0) as total_pl
            FROM trade_history
            WHERE user_id = %s
        """, (user_id,))
        
        result = cur.fetchone()
        
        cur.close()
        conn.close()
        
        return float(result[0]) if result else 0.0
    
    def get_inactive_users(self, hours: int = 1) -> List[Dict]:
        """Get users who haven't been active in the last X hours"""
        conn = self.get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            SELECT user_id, username, language
            FROM users
            WHERE last_activity < NOW() - INTERVAL '1 hour' * %s
            OR last_activity IS NULL
        """, (hours,))
        
        users = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return [dict(u) for u in users]
    
    def update_last_welcome(self, user_id: int):
        """Update user's last welcome timestamp"""
        conn = self.get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            UPDATE users
            SET last_welcome = %s
            WHERE user_id = %s
        """, (datetime.now(), user_id))
        
        conn.commit()
        cur.close()
        conn.close()

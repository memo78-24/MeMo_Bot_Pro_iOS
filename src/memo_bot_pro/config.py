import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    binance_api_key: Optional[str] = None
    binance_api_secret: Optional[str] = None
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    mock_mode: bool = True
    admin_user_ids: list = None
    
    def __post_init__(self):
        if self.admin_user_ids is None:
            self.admin_user_ids = []

    @classmethod
    def from_env(cls) -> 'Config':
        # Parse admin user IDs from environment
        admin_ids_str = os.getenv('TELEGRAM_ADMIN_IDS', '')
        admin_user_ids = [int(uid.strip()) for uid in admin_ids_str.split(',') if uid.strip().isdigit()]
        
        return cls(
            binance_api_key=os.getenv('BINANCE_API_KEY'),
            binance_api_secret=os.getenv('BINANCE_API_SECRET'),
            telegram_bot_token=os.getenv('TELEGRAM_BOT_TOKEN'),
            telegram_chat_id=os.getenv('TELEGRAM_CHAT_ID'),
            mock_mode=os.getenv('MOCK_MODE', 'true').lower() == 'true',
            admin_user_ids=admin_user_ids
        )

    def validate_binance(self) -> bool:
        return bool(self.binance_api_key and self.binance_api_secret)

    def validate_telegram(self) -> bool:
        return bool(self.telegram_bot_token)
    
    def is_admin(self, user_id: int) -> bool:
        """Check if a user is an admin"""
        return user_id in self.admin_user_ids

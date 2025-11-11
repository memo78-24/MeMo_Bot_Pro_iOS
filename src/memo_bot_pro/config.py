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

    @classmethod
    def from_env(cls) -> 'Config':
        return cls(
            binance_api_key=os.getenv('BINANCE_API_KEY'),
            binance_api_secret=os.getenv('BINANCE_API_SECRET'),
            telegram_bot_token=os.getenv('TELEGRAM_BOT_TOKEN'),
            telegram_chat_id=os.getenv('TELEGRAM_CHAT_ID'),
            mock_mode=os.getenv('MOCK_MODE', 'true').lower() == 'true'
        )

    def validate_binance(self) -> bool:
        return bool(self.binance_api_key and self.binance_api_secret)

    def validate_telegram(self) -> bool:
        return bool(self.telegram_bot_token)

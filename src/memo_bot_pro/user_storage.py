import openpyxl
from openpyxl import Workbook
import os
from datetime import datetime
from typing import Dict, Optional

STORAGE_FILE = 'user_settings.xlsx'

class UserStorage:
    def __init__(self):
        self.file_path = STORAGE_FILE
        self._init_storage()
    
    def _init_storage(self):
        if not os.path.exists(self.file_path):
            wb = Workbook()
            ws = wb.active
            ws.title = "User Settings"
            ws.append(['User ID', 'Username', 'Language', 'Auto Signals', 'Timezone', 'Last Updated'])
            wb.save(self.file_path)
    
    def get_user_settings(self, user_id: int) -> Optional[Dict]:
        try:
            wb = openpyxl.load_workbook(self.file_path)
            ws = wb['User Settings']
            
            for row in ws.iter_rows(min_row=2, values_only=False):
                if row[0].value == user_id:
                    return {
                        'user_id': row[0].value,
                        'username': row[1].value,
                        'language': row[2].value or 'en',
                        'auto_signals': row[3].value == 'True',
                        'timezone': row[4].value or 'UTC',
                        'last_updated': row[5].value
                    }
            return None
        except Exception as e:
            print(f"Error reading user settings: {e}")
            return None
    
    def save_user_settings(self, user_id: int, username: str, settings: Dict):
        try:
            wb = openpyxl.load_workbook(self.file_path)
            ws = wb['User Settings']
            
            row_to_update = None
            for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=False), start=2):
                if row[0].value == user_id:
                    row_to_update = idx
                    break
            
            language = settings.get('language', 'en')
            auto_signals = str(settings.get('auto_signals', False))
            timezone = settings.get('timezone', 'UTC')
            last_updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            if row_to_update:
                ws[f'A{row_to_update}'] = user_id
                ws[f'B{row_to_update}'] = username
                ws[f'C{row_to_update}'] = language
                ws[f'D{row_to_update}'] = auto_signals
                ws[f'E{row_to_update}'] = timezone
                ws[f'F{row_to_update}'] = last_updated
            else:
                ws.append([user_id, username, language, auto_signals, timezone, last_updated])
            
            wb.save(self.file_path)
            return True
        except Exception as e:
            print(f"Error saving user settings: {e}")
            return False
    
    def get_all_users(self):
        """Get all users from storage"""
        users = []
        try:
            wb = openpyxl.load_workbook(self.file_path)
            ws = wb['User Settings']
            
            for row in ws.iter_rows(min_row=2, values_only=True):
                if row[0]:
                    users.append({
                        'user_id': row[0],
                        'username': row[1],
                        'language': row[2] or 'en',
                        'auto_signals': row[3] == 'True',
                        'timezone': row[4] or 'UTC'
                    })
        except Exception as e:
            print(f"Error getting all users: {e}")
        
        return users
    
    def get_all_users_with_auto_signals(self):
        users = []
        try:
            wb = openpyxl.load_workbook(self.file_path)
            ws = wb['User Settings']
            
            for row in ws.iter_rows(min_row=2, values_only=True):
                if row[3] == 'True':
                    users.append({
                        'user_id': row[0],
                        'username': row[1],
                        'language': row[2] or 'en'
                    })
        except Exception as e:
            print(f"Error getting users: {e}")
        
        return users

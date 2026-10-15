"""
Интеграция с Google Sheets для синхронизации данных CRM
"""
import os
from typing import List, Dict, Any, Optional
from database import Database

try:
    from google.oauth2.credentials import Credentials
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_SHEETS_AVAILABLE = True
except ImportError:
    GOOGLE_SHEETS_AVAILABLE = False
    print("⚠️ Google Sheets библиотеки не установлены. Установите: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")


class GoogleSheetsSync:
    """Синхронизация данных CRM с Google Sheets"""
    
    def __init__(self, credentials_file: str = None, spreadsheet_id: str = None):
        self.credentials_file = credentials_file or os.getenv("GOOGLE_CREDENTIALS_FILE")
        self.spreadsheet_id = spreadsheet_id or os.getenv("GOOGLE_SHEET_ID")
        self.service = None
        self.db = Database()
        
        if GOOGLE_SHEETS_AVAILABLE and self.credentials_file:
            self._init_service()
    
    def _init_service(self):
        """Инициализация Google Sheets API"""
        try:
            if os.path.exists(self.credentials_file):
                creds = service_account.Credentials.from_service_account_file(
                    self.credentials_file,
                    scopes=['https://www.googleapis.com/auth/spreadsheets']
                )
                self.service = build('sheets', 'v4', credentials=creds)
                print("✅ Google Sheets API инициализирован")
            else:
                print(f"⚠️ Файл credentials не найден: {self.credentials_file}")
        except Exception as e:
            print(f"❌ Ошибка инициализации Google Sheets: {e}")
    
    async def sync_client(self, client_id: int) -> bool:
        """Синхронизировать клиента с Google Sheets"""
        if not self.service or not self.spreadsheet_id:
            return False
        
        try:
            client = await self.db.get_client(client_id)
            if not client:
                return False
            
            # Получаем или создаем лист "Клиенты"
            sheet_name = "Клиенты"
            await self._ensure_sheet_exists(sheet_name, ["ID", "Имя", "Телефон", "Email", "Компания", "Заметки", "Создан"])
            
            # Ищем существующую запись
            existing_row = await self._find_row(sheet_name, client_id, 0)
            
            row_data = [
                client['id'],
                client['name'],
                client.get('phone', ''),
                client.get('email', ''),
                client.get('company', ''),
                client.get('notes', ''),
                client['created_at']
            ]
            
            if existing_row:
                # Обновляем существующую строку
                range_name = f"{sheet_name}!A{existing_row}:G{existing_row}"
                self.service.spreadsheets().values().update(
                    spreadsheetId=self.spreadsheet_id,
                    range=range_name,
                    valueInputOption='RAW',
                    body={'values': [row_data]}
                ).execute()
            else:
                # Добавляем новую строку
                range_name = f"{sheet_name}!A:G"
                self.service.spreadsheets().values().append(
                    spreadsheetId=self.spreadsheet_id,
                    range=range_name,
                    valueInputOption='RAW',
                    insertDataOption='INSERT_ROWS',
                    body={'values': [row_data]}
                ).execute()
            
            print(f"✅ Клиент {client_id} синхронизирован с Google Sheets")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка синхронизации клиента: {e}")
            return False
    
    async def sync_deal(self, deal_id: int) -> bool:
        """Синхронизировать сделку с Google Sheets"""
        if not self.service or not self.spreadsheet_id:
            return False
        
        try:
            deal = await self.db.get_deal(deal_id)
            if not deal:
                return False
            
            client = await self.db.get_client(deal['client_id'])
            client_name = client['name'] if client else f"ID: {deal['client_id']}"
            
            sheet_name = "Сделки"
            await self._ensure_sheet_exists(sheet_name, ["ID", "Клиент", "Название", "Сумма", "Статус", "Описание", "Создана"])
            
            existing_row = await self._find_row(sheet_name, deal_id, 0)
            
            row_data = [
                deal['id'],
                client_name,
                deal['title'],
                deal['amount'],
                deal['status'],
                deal.get('description', ''),
                deal['created_at']
            ]
            
            if existing_row:
                range_name = f"{sheet_name}!A{existing_row}:G{existing_row}"
                self.service.spreadsheets().values().update(
                    spreadsheetId=self.spreadsheet_id,
                    range=range_name,
                    valueInputOption='RAW',
                    body={'values': [row_data]}
                ).execute()
            else:
                range_name = f"{sheet_name}!A:G"
                self.service.spreadsheets().values().append(
                    spreadsheetId=self.spreadsheet_id,
                    range=range_name,
                    valueInputOption='RAW',
                    insertDataOption='INSERT_ROWS',
                    body={'values': [row_data]}
                ).execute()
            
            print(f"✅ Сделка {deal_id} синхронизирована с Google Sheets")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка синхронизации сделки: {e}")
            return False
    
    async def _ensure_sheet_exists(self, sheet_name: str, headers: List[str]):
        """Убедиться, что лист существует и имеет заголовки"""
        try:
            # Получаем список листов
            sheet_metadata = self.service.spreadsheets().get(
                spreadsheetId=self.spreadsheet_id
            ).execute()
            
            sheet_exists = any(sheet['properties']['title'] == sheet_name 
                             for sheet in sheet_metadata.get('sheets', []))
            
            if not sheet_exists:
                # Создаем новый лист
                requests = [{
                    'addSheet': {
                        'properties': {
                            'title': sheet_name
                        }
                    }
                }]
                self.service.spreadsheets().batchUpdate(
                    spreadsheetId=self.spreadsheet_id,
                    body={'requests': requests}
                ).execute()
            
            # Проверяем заголовки
            range_name = f"{sheet_name}!A1:{chr(64 + len(headers))}1"
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            if not values or values[0] != headers:
                # Устанавливаем заголовки
                self.service.spreadsheets().values().update(
                    spreadsheetId=self.spreadsheet_id,
                    range=f"{sheet_name}!A1:{chr(64 + len(headers))}1",
                    valueInputOption='RAW',
                    body={'values': [headers]}
                ).execute()
                
        except Exception as e:
            print(f"❌ Ошибка создания листа: {e}")
    
    async def _find_row(self, sheet_name: str, record_id: int, column_index: int = 0) -> Optional[int]:
        """Найти строку по ID записи"""
        try:
            range_name = f"{sheet_name}!A:A"
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            for i, row in enumerate(values[1:], start=2):  # Пропускаем заголовок
                if row and len(row) > column_index and str(row[column_index]) == str(record_id):
                    return i
            return None
        except Exception as e:
            print(f"❌ Ошибка поиска строки: {e}")
            return None


# Упрощенная версия без Google API (для тестирования)
class MockGoogleSheetsSync:
    """Мок-версия для тестирования без Google API"""
    
    def __init__(self, *args, **kwargs):
        print("⚠️ Используется мок-версия Google Sheets (данные не синхронизируются)")
    
    async def sync_client(self, client_id: int) -> bool:
        print(f"📊 [Мок] Клиент {client_id} был бы синхронизирован с Google Sheets")
        return True
    
    async def sync_deal(self, deal_id: int) -> bool:
        print(f"📊 [Мок] Сделка {deal_id} была бы синхронизирована с Google Sheets")
        return True


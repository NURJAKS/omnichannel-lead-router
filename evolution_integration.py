"""
Интеграция с Evolution API вместо whatsapp-web.js
Быстрее, стабильнее, без браузера!
n8n НЕ нужен - используем чисто кодом!
"""

import requests
import asyncio
from typing import Dict, Any, Optional
from database import Database


class EvolutionAPIIntegration:
    """Интеграция с Evolution API - чисто кодом, без n8n!"""
    
    def __init__(self, 
                 api_url: str = "http://localhost:8080",
                 api_key: str = None,
                 instance_name: str = "crm-instance",
                 database: Database = None):
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key or "evolution-api-key"  # Замените на ваш ключ
        self.instance_name = instance_name
        self.db = database or Database()
        self.headers = {
            "apikey": self.api_key,
            "Content-Type": "application/json"
        }
    
    def create_instance(self) -> Dict[str, Any]:
        """Создать инстанс WhatsApp"""
        url = f"{self.api_url}/instance/create"
        data = {
            "instanceName": self.instance_name,
            "token": self.api_key,
            "qrcode": True,
            "integration": "WHATSAPP-BAILEYS"
        }
        
        try:
            response = requests.post(url, json=data, headers=self.headers, timeout=10)
            return response.json()
        except Exception as e:
            return {"error": str(e), "message": "Проверьте, что Evolution API запущен"}
    
    def get_qr_code(self) -> Optional[str]:
        """Получить QR код для подключения"""
        url = f"{self.api_url}/instance/connect/{self.instance_name}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            data = response.json()
            # Evolution API возвращает QR в разных форматах
            if isinstance(data, dict):
                qr_data = data.get('qrcode', {})
                if isinstance(qr_data, dict):
                    return qr_data.get('base64') or qr_data.get('code')
                return qr_data
            return data
        except Exception as e:
            print(f"Ошибка получения QR кода: {e}")
            return None
    
    def get_instance_status(self) -> Dict[str, Any]:
        """Получить статус инстанса"""
        url = f"{self.api_url}/instance/fetchInstances"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=5)
            instances = response.json()
            
            if isinstance(instances, list):
                for instance in instances:
                    if instance.get('instanceName') == self.instance_name:
                        return instance
            
            return {"status": "not_found", "instances": instances}
        except Exception as e:
            return {"error": str(e), "message": "Проверьте, что Evolution API запущен на порту 8080"}
    
    def send_message(self, phone: str, message: str) -> Dict[str, Any]:
        """Отправить сообщение"""
        url = f"{self.api_url}/message/sendText/{self.instance_name}"
        
        # Форматируем номер (убираем + и пробелы)
        import re
        formatted_phone = re.sub(r'[^0-9]', '', str(phone))
        
        data = {
            "number": formatted_phone,
            "text": message
        }
        
        try:
            response = requests.post(url, json=data, headers=self.headers, timeout=10)
            return response.json()
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def handle_incoming_message(self, phone: str, message: str, sender_name: str = None):
        """Обработать входящее сообщение"""
        # Ищем клиента
        clients = await self.db.search_clients(phone)
        client = clients[0] if clients else None
        client_id = client['id'] if client else None
        
        # Сохраняем в историю
        import aiosqlite
        async with aiosqlite.connect(self.db.db_path) as db:
            await db.execute("""
                INSERT INTO interactions (client_id, channel, message_type, message)
                VALUES (?, 'whatsapp', 'incoming', ?)
            """, (client_id, message))
            await db.commit()
        
        # Генерируем ответ (простая логика)
        if not client:
            response_text = f"Добро пожаловать, {sender_name or 'друг'}! 👋\n\nОтправьте ваше имя:"
        else:
            response_text = f"Привет, {client['name']}! Чем могу помочь?"
        
        # Отправляем ответ
        result = self.send_message(phone, response_text)
        return result
    
    def check_health(self) -> Dict[str, Any]:
        """Проверить здоровье API"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            return response.json()
        except Exception as e:
            return {"status": "error", "error": str(e)}


def setup_evolution_webhook(api_url: str, api_key: str, instance_name: str, webhook_url: str):
    """Настроить webhook для получения сообщений"""
    url = f"{api_url}/webhook/set/{instance_name}"
    data = {
        "url": webhook_url,
        "webhook_by_events": False,
        "webhook_base64": False,
        "events": ["MESSAGES_UPSERT", "MESSAGES_UPDATE"]
    }
    headers = {
        "apikey": api_key,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


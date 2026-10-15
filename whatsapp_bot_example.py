"""
Пример реализации WhatsApp бота (НЕОФИЦИАЛЬНЫЙ способ)
⚠️ ВНИМАНИЕ: Это нарушает ToS WhatsApp и может привести к блокировке аккаунта!
Используйте только для тестирования и понимания процесса.

Для production используйте WhatsApp Business API через официальных провайдеров.
"""

# Вариант 1: Через whatsapp-web.js (Node.js) - НЕ РЕКОМЕНДУЕТСЯ
# Нужен Node.js и библиотека whatsapp-web.js

# Вариант 2: Через pywhatkit (Python) - ОЧЕНЬ ОГРАНИЧЕННЫЙ
# from pywhatkit import sendwhatmsg
# import pywhatkit as pwk
# 
# # Отправка сообщения (только в определенное время)
# pwk.sendwhatmsg("+1234567890", "Привет из CRM!", 14, 30)

# Вариант 3: Через Selenium + WhatsApp Web - НЕСТАБИЛЬНО
# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
# 
# driver = webdriver.Chrome()
# driver.get("https://web.whatsapp.com")
# # Нужно вручную отсканировать QR код
# # Затем можно отправлять сообщения

# Вариант 4: Через готовый сервис (РЕКОМЕНДУЕТСЯ для production)
# Пример интеграции с Wazzup API

import requests
import os
from typing import Optional

class WhatsAppWazzup:
    """
    Интеграция с WhatsApp через Wazzup API
    Требуется регистрация на wazzup24.ru
    """
    
    def __init__(self, api_key: str, channel_id: str):
        self.api_key = api_key
        self.channel_id = channel_id
        self.base_url = "https://api.wazzup24.com/v3"
    
    def send_message(self, phone: str, message: str) -> bool:
        """Отправить сообщение в WhatsApp"""
        url = f"{self.base_url}/messages"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "channelId": self.channel_id,
            "chatType": "whatsapp",
            "chatId": phone,
            "text": message
        }
        
        try:
            response = requests.post(url, json=data, headers=headers)
            return response.status_code == 200
        except Exception as e:
            print(f"Ошибка отправки: {e}")
            return False
    
    def receive_messages(self):
        """Получить входящие сообщения (webhook)"""
        # Нужно настроить webhook на стороне Wazzup
        pass


# Пример использования с текущей CRM
class WhatsAppCRMAdapter:
    """
    Адаптер для подключения WhatsApp к существующей CRM
    """
    
    def __init__(self, whatsapp_client, database):
        self.whatsapp = whatsapp_client
        self.db = database
    
    async def handle_incoming_message(self, phone: str, message: str):
        """Обработать входящее сообщение"""
        # Найти клиента по телефону
        clients = await self.db.search_clients(phone)
        
        if clients:
            client = clients[0]
            # Сохранить сообщение в историю взаимодействий
            # (нужно добавить таблицу interactions)
            response = f"Привет, {client['name']}! Чем могу помочь?"
        else:
            response = "Добро пожаловать! Для начала работы отправьте ваше имя."
        
        # Отправить ответ
        self.whatsapp.send_message(phone, response)
    
    async def send_client_notification(self, client_id: int, message: str):
        """Отправить уведомление клиенту"""
        client = await self.db.get_client(client_id)
        if client and client.get('phone'):
            self.whatsapp.send_message(client['phone'], message)


# ПРИМЕР ИНТЕГРАЦИИ С FASTAPI (для webhook)
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post("/whatsapp/webhook")
async def whatsapp_webhook(request: Request):
    data = await request.json()
    
    # Обработка входящего сообщения
    phone = data.get('from')
    message = data.get('text')
    
    # Интеграция с CRM
    adapter = WhatsAppCRMAdapter(whatsapp_client, database)
    await adapter.handle_incoming_message(phone, message)
    
    return JSONResponse({"status": "ok"})
"""


"""
ВАЖНО: Для production используйте официальный WhatsApp Business API!

Официальные провайдеры:
1. Twilio (twilio.com) - от $0.005 за сообщение
2. MessageBird (messagebird.com) - от €0.005 за сообщение  
3. 360dialog (360dialog.com) - от €49/мес
4. Wazzup (wazzup24.ru) - от 990₽/мес (Россия)

Процесс:
1. Зарегистрироваться у провайдера
2. Получить API ключ
3. Настроить webhook для входящих сообщений
4. Интегрировать с вашей CRM
"""


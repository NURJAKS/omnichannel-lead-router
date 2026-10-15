"""
Интеграция WhatsApp с CRM через whatsapp-web.js сервис
Умный бот-менеджер с автоматическими ответами
"""

import requests
import asyncio
import re
from typing import Optional, Dict, Any
from database import Database
from datetime import datetime


class WhatsAppBotManager:
    """Умный WhatsApp бот-менеджер с автоматическими ответами"""
    
    def __init__(self, whatsapp_api_url: str = "http://localhost:3001", database: Database = None):
        self.api_url = whatsapp_api_url
        self.db = database or Database()
        self.user_states = {}  # Состояния пользователей для диалогов
    
    def send_message(self, phone: str, message: str) -> Dict[str, Any]:
        """Отправить сообщение в WhatsApp"""
        try:
            response = requests.post(
                f"{self.api_url}/send",
                json={"phone": phone, "message": message},
                timeout=10
            )
            return response.json()
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def save_interaction(self, client_id: Optional[int], phone: str, 
                              message: str, response: str = None):
        """Сохранить взаимодействие в историю"""
        import aiosqlite
        async with aiosqlite.connect(self.db.db_path) as db:
            await db.execute("""
                INSERT INTO interactions (client_id, channel, message_type, message, response)
                VALUES (?, 'whatsapp', 'incoming', ?, ?)
            """, (client_id, message, response))
            await db.commit()
    
    async def handle_incoming_message(self, phone: str, message: str, sender_name: str = None):
        """Обработать входящее сообщение - умный бот-менеджер"""
        message_lower = message.lower().strip()
        
        # Ищем клиента по телефону
        clients = await self.db.search_clients(phone)
        client = clients[0] if clients else None
        client_id = client['id'] if client else None
        
        # Сохраняем входящее сообщение
        await self.save_interaction(client_id, phone, message)
        
        # Получаем состояние пользователя
        user_state = self.user_states.get(phone, {})
        state = user_state.get('state', 'idle')
        
        # Обработка команд
        if message_lower in ['привет', 'здравствуй', 'hi', 'hello', 'начать', '/start']:
            response_text = self._handle_greeting(client, sender_name)
        
        elif message_lower in ['помощь', 'help', 'команды', '/help']:
            response_text = self._handle_help(client)
        
        elif message_lower in ['статус', 'status', 'мои заказы', 'мои сделки']:
            response_text = await self._handle_status(client_id)
        
        elif message_lower in ['контакты', 'контакт', 'телефон', 'адрес']:
            response_text = self._handle_contacts()
        
        elif state == 'waiting_name':
            # Регистрация нового клиента
            name = message.strip()
            client_id = await self.db.add_client(name=name, phone=phone)
            self.user_states[phone] = {'state': 'waiting_email', 'name': name, 'client_id': client_id}
            response_text = f"Отлично, {name}! 👋\n\nТеперь отправьте ваш email (или напишите 'пропустить'):"
        
        elif state == 'waiting_email':
            email = None if message_lower in ['пропустить', 'skip', 'нет'] else message.strip()
            await self.db.update_client(self.user_states[phone]['client_id'], email=email)
            self.user_states[phone]['state'] = 'waiting_company'
            response_text = "Спасибо! Теперь отправьте название компании (или 'пропустить'):"
        
        elif state == 'waiting_company':
            company = None if message_lower in ['пропустить', 'skip', 'нет'] else message.strip()
            await self.db.update_client(self.user_states[phone]['client_id'], company=company)
            self.user_states[phone] = {'state': 'idle'}
            response_text = "✅ Регистрация завершена! Чем могу помочь?"
        
        elif not client:
            # Новый клиент - начинаем регистрацию
            self.user_states[phone] = {'state': 'waiting_name'}
            response_text = (
                f"Добро пожаловать, {sender_name or 'друг'}! 👋\n\n"
                "Я ваш персональный менеджер. Для начала работы отправьте ваше имя:"
            )
        
        else:
            # Обычное сообщение - умный ответ
            response_text = await self._handle_general_message(client, message, message_lower)
        
        # Отправляем ответ
        result = self.send_message(phone, response_text)
        
        # Сохраняем ответ в историю
        await self.save_interaction(client_id, phone, message, response_text)
        
        return result
    
    def _handle_greeting(self, client, sender_name: str) -> str:
        """Обработка приветствия"""
        if client:
            return (
                f"Привет, {client['name']}! 👋\n\n"
                "Чем могу помочь?\n\n"
                "Доступные команды:\n"
                "• Статус - мои заказы/сделки\n"
                "• Контакты - контактная информация\n"
                "• Помощь - список команд"
            )
        else:
            return (
                f"Привет, {sender_name or 'друг'}! 👋\n\n"
                "Я ваш персональный менеджер. Для начала работы отправьте ваше имя:"
            )
    
    def _handle_help(self, client) -> str:
        """Показать помощь"""
        return (
            "📋 Доступные команды:\n\n"
            "• Привет - начать диалог\n"
            "• Статус - мои заказы и сделки\n"
            "• Контакты - контактная информация\n"
            "• Помощь - эта справка\n\n"
            "Просто напишите ваш вопрос, и я помогу!"
        )
    
    async def _handle_status(self, client_id: Optional[int]) -> str:
        """Показать статус заказов/сделок"""
        if not client_id:
            return "Вы еще не зарегистрированы. Отправьте 'Привет' для начала."
        
        deals = await self.db.get_deals_by_client(client_id)
        
        if not deals:
            return "У вас пока нет активных сделок. Хотите создать новую?"
        
        text = "📊 Ваши сделки:\n\n"
        for deal in deals[:5]:
            text += f"• {deal['title']}\n"
            text += f"  💰 {deal['amount']:,.2f} ₽\n"
            text += f"  📊 Статус: {deal['status']}\n\n"
        
        if len(deals) > 5:
            text += f"... и еще {len(deals) - 5} сделок"
        
        return text
    
    def _handle_contacts(self) -> str:
        """Показать контакты"""
        return (
            "📞 Контактная информация:\n\n"
            "Телефон: +7 (XXX) XXX-XX-XX\n"
            "Email: info@example.com\n"
            "Адрес: Ваш адрес\n\n"
            "Рабочие часы: Пн-Пт 9:00-18:00"
        )
    
    async def _handle_general_message(self, client: Dict, message: str, message_lower: str) -> str:
        """Обработка общего сообщения - умные ответы"""
        # Поиск ключевых слов
        if any(word in message_lower for word in ['цена', 'стоимость', 'сколько', 'price', 'cost']):
            return "Для уточнения цены, пожалуйста, укажите интересующий вас товар/услугу. Я подготовлю расчет!"
        
        elif any(word in message_lower for word in ['заказ', 'купить', 'оформить', 'order', 'buy']):
            return "Отлично! Для оформления заказа укажите:\n• Название товара/услуги\n• Количество\n• Адрес доставки (если нужно)"
        
        elif any(word in message_lower for word in ['доставка', 'delivery', 'когда', 'срок']):
            return "Срок доставки зависит от вашего региона. Обычно 1-3 рабочих дня. Уточню детали и сообщу точный срок!"
        
        elif any(word in message_lower for word in ['спасибо', 'благодарю', 'thanks', 'thank you']):
            return "Пожалуйста! Рад помочь! 😊\n\nЕсли будут вопросы - обращайтесь!"
        
        else:
            return (
                f"Спасибо за сообщение, {client['name']}! 👍\n\n"
                "Я передам ваш запрос менеджеру, и мы свяжемся с вами в ближайшее время.\n\n"
                "Или напишите:\n"
                "• Статус - для проверки заказов\n"
                "• Помощь - для списка команд"
            )


# Обратная совместимость
WhatsAppIntegration = WhatsAppBotManager
    
    async def send_client_notification(self, client_id: int, message: str) -> bool:
        """Отправить уведомление клиенту"""
        client = await self.db.get_client(client_id)
        if client and client.get('phone'):
            result = self.send_message(client['phone'], message)
            return result.get('success', False)
        return False
    
    def get_status(self) -> Dict[str, Any]:
        """Получить статус WhatsApp подключения"""
        try:
            response = requests.get(f"{self.api_url}/status", timeout=5)
            return response.json()
        except Exception as e:
            return {"status": "error", "error": str(e)}


# Интеграция с FastAPI для webhook
from fastapi import Request
from fastapi.responses import JSONResponse

def setup_whatsapp_routes(app, whatsapp_integration: WhatsAppBotManager):
    """Настройка роутов для WhatsApp в FastAPI"""
    
    @app.post("/api/whatsapp/message")
    async def receive_whatsapp_message(request: Request):
        """Получить входящее сообщение из WhatsApp"""
        data = await request.json()
        
        phone = data.get('from')
        message = data.get('message')
        sender_name = data.get('fromName')
        
        if not phone or not message:
            return JSONResponse({"error": "Нужны from и message"}, status_code=400)
        
        # Обрабатываем сообщение
        result = await whatsapp_integration.handle_incoming_message(
            phone, message, sender_name
        )
        
        return JSONResponse({"status": "ok", "result": result})
    
    @app.post("/api/whatsapp/send")
    async def send_whatsapp_message(request: Request):
        """Отправить сообщение через WhatsApp"""
        data = await request.json()
        
        phone = data.get('phone')
        message = data.get('message')
        
        if not phone or not message:
            return JSONResponse({"error": "Нужны phone и message"}, status_code=400)
        
        result = whatsapp_integration.send_message(phone, message)
        return JSONResponse(result)
    
    @app.get("/api/whatsapp/status")
    async def whatsapp_status():
        """Статус WhatsApp подключения"""
        status = whatsapp_integration.get_status()
        return JSONResponse(status)


# Пример использования в web.py:
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from whatsapp_integration import WhatsAppIntegration, setup_whatsapp_routes
from database import Database

app = FastAPI()
db = Database()
whatsapp = WhatsAppIntegration(database=db)

# Подключаем WhatsApp роуты
setup_whatsapp_routes(app, whatsapp)

# Теперь можно отправлять сообщения клиентам:
# POST /api/whatsapp/send
# {
#   "phone": "+79991234567",
#   "message": "Привет из CRM!"
# }
"""


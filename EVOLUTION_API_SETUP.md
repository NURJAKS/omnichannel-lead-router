# 🚀 Evolution API - Установка и использование

## ❓ Нужен ли n8n?

### **Короткий ответ: НЕТ, не нужен!** ✅

**Evolution API можно использовать:**
- ✅ **Чисто кодом** (REST API) - рекомендуемый способ
- ✅ **Через n8n** (визуальный редактор) - опционально
- ✅ **Через любые HTTP запросы** - Python, Node.js, curl

**n8n нужен только если:**
- Хотите визуальный редактор для автоматизации
- Нужны сложные workflow без кода
- Команда не программисты

**Для вашей CRM: используйте чисто кодом!** 🎯

---

## 🔍 Поиск Evolution API

Если Evolution API уже установлен, проверьте:

```bash
# Поиск в системе
find /opt -name "*evolution*" 2>/dev/null
find /usr/local -name "*evolution*" 2>/dev/null

# Docker контейнеры
docker ps -a | grep evolution
docker images | grep evolution

# Процессы
ps aux | grep evolution
```

---

## 🚀 Установка Evolution API (если нет)

### **Вариант 1: Docker (рекомендуется)**

```bash
# Создайте директорию
mkdir -p /opt/evolution-api
cd /opt/evolution-api

# Запустите через Docker
docker run -d \
  --name evolution-api \
  -p 8080:8080 \
  -e AUTHENTICATION_API_KEY=your-secret-key-here \
  -e CONFIG_SESSION_PHONE_CLIENT=Chrome \
  -e CONFIG_SESSION_PHONE_NAME=CRM \
  -v $(pwd)/evolution-instances:/evolution/instances \
  -v $(pwd)/evolution-store:/evolution/store \
  atendai/evolution-api:latest
```

### **Вариант 2: Docker Compose (удобнее)**

Создайте `/opt/evolution-api/docker-compose.yml`:

```yaml
version: '3.8'

services:
  evolution-api:
    image: atendai/evolution-api:latest
    container_name: evolution-api
    ports:
      - "8080:8080"
    environment:
      - AUTHENTICATION_API_KEY=your-secret-key-here
      - CONFIG_SESSION_PHONE_CLIENT=Chrome
      - CONFIG_SESSION_PHONE_NAME=CRM
    volumes:
      - ./evolution-instances:/evolution/instances
      - ./evolution-store:/evolution/store
    restart: unless-stopped
```

Запуск:
```bash
cd /opt/evolution-api
docker-compose up -d
```

---

## ✅ Проверка работы

```bash
# Проверка статуса
curl http://localhost:8080/health

# Должно вернуть:
# {"status":"ok"}
```

---

## 🔗 Интеграция с вашей CRM

### **1. Обновление whatsapp_integration.py**

Создайте новый файл `evolution_integration.py`:

```python
"""
Интеграция с Evolution API вместо whatsapp-web.js
Быстрее, стабильнее, без браузера!
"""

import requests
import asyncio
from typing import Dict, Any, Optional
from database import Database


class EvolutionAPIIntegration:
    """Интеграция с Evolution API"""
    
    def __init__(self, 
                 api_url: str = "http://localhost:8080",
                 api_key: str = "your-secret-key-here",
                 instance_name: str = "crm-instance",
                 database: Database = None):
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.instance_name = instance_name
        self.db = database or Database()
        self.headers = {
            "apikey": api_key,
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
            return {"error": str(e)}
    
    def get_qr_code(self) -> Optional[str]:
        """Получить QR код для подключения"""
        url = f"{self.api_url}/instance/connect/{self.instance_name}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            data = response.json()
            return data.get('qrcode', {}).get('base64')
        except Exception as e:
            print(f"Ошибка получения QR кода: {e}")
            return None
    
    def get_instance_status(self) -> Dict[str, Any]:
        """Получить статус инстанса"""
        url = f"{self.api_url}/instance/fetchInstances"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=5)
            instances = response.json()
            
            for instance in instances:
                if instance.get('instanceName') == self.instance_name:
                    return instance
            
            return {"status": "not_found"}
        except Exception as e:
            return {"error": str(e)}
    
    def send_message(self, phone: str, message: str) -> Dict[str, Any]:
        """Отправить сообщение"""
        url = f"{self.api_url}/message/sendText/{self.instance_name}"
        data = {
            "number": phone,
            "text": message
        }
        
        try:
            response = requests.post(url, json=data, headers=self.headers, timeout=10)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    async def handle_incoming_message(self, phone: str, message: str, sender_name: str = None):
        """Обработать входящее сообщение (используйте webhook)"""
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
        
        # Генерируем ответ (используйте логику из WhatsAppBotManager)
        if not client:
            response_text = f"Добро пожаловать, {sender_name or 'друг'}! 👋\n\nОтправьте ваше имя:"
        else:
            response_text = f"Привет, {client['name']}! Чем могу помочь?"
        
        # Отправляем ответ
        result = self.send_message(phone, response_text)
        return result


# Настройка webhook для входящих сообщений
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
```

### **2. Обновление web.py для Evolution API**

```python
from evolution_integration import EvolutionAPIIntegration, setup_evolution_webhook

# Инициализация Evolution API
evolution = EvolutionAPIIntegration(
    api_url="http://localhost:8080",
    api_key="your-secret-key-here",
    instance_name="crm-instance",
    database=db
)

# Настройка webhook (один раз)
# setup_evolution_webhook(
#     "http://localhost:8080",
#     "your-secret-key-here",
#     "crm-instance",
#     "http://your-server:8000/api/evolution/webhook"
# )

# Роут для webhook
@app.post("/api/evolution/webhook")
async def evolution_webhook(request: Request):
    """Получить входящее сообщение из Evolution API"""
    data = await request.json()
    
    # Evolution API отправляет события
    if data.get('event') == 'messages.upsert':
        message_data = data.get('data', {})
        phone = message_data.get('key', {}).get('remoteJid', '').replace('@s.whatsapp.net', '')
        message = message_data.get('message', {}).get('conversation', '')
        
        if phone and message:
            await evolution.handle_incoming_message(phone, message)
    
    return JSONResponse({"status": "ok"})
```

---

## 📋 Пошаговая настройка

### **1. Запустите Evolution API:**

```bash
cd /opt/evolution-api
docker-compose up -d
```

### **2. Создайте инстанс:**

```python
from evolution_integration import EvolutionAPIIntegration

evolution = EvolutionAPIIntegration()
result = evolution.create_instance()
print(result)
```

### **3. Получите QR код:**

```python
qr = evolution.get_qr_code()
# Сохраните QR код или покажите пользователю
```

### **4. Настройте webhook:**

```python
setup_evolution_webhook(
    "http://localhost:8080",
    "your-secret-key",
    "crm-instance",
    "http://your-server:8000/api/evolution/webhook"
)
```

### **5. Отправьте тестовое сообщение:**

```python
result = evolution.send_message("79991234567", "Привет из CRM!")
print(result)
```

---

## 🎯 Преимущества Evolution API

### **vs whatsapp-web.js:**

| Критерий | whatsapp-web.js | Evolution API |
|----------|-----------------|---------------|
| **Время запуска** | 30-60 сек | 2-5 сек ⚡ |
| **Требует браузер** | Да | Нет ✅ |
| **Стабильность** | ⭐⭐ | ⭐⭐⭐⭐ |
| **REST API** | Ограниченный | Полный ✅ |
| **Множество инстансов** | Нет | Да ✅ |
| **Production ready** | Нет | Да ✅ |

---

## ❌ n8n НЕ нужен!

**Вы можете:**
- ✅ Использовать Evolution API напрямую через REST API
- ✅ Писать код на Python/Node.js
- ✅ Использовать любые HTTP запросы
- ✅ Интегрировать с вашей CRM

**n8n нужен только для:**
- Визуального редактора workflow
- Автоматизации без кода
- Если команда не программисты

**Для вашей CRM: используйте Evolution API напрямую!** 🎯

---

## 🔧 Быстрый старт

```bash
# 1. Запустите Evolution API
cd /opt/evolution-api
docker-compose up -d

# 2. Проверьте
curl http://localhost:8080/health

# 3. Используйте в коде
python -c "
from evolution_integration import EvolutionAPIIntegration
evolution = EvolutionAPIIntegration()
print(evolution.get_instance_status())
"
```

---

## 📚 Документация Evolution API

- Официальный сайт: https://evolution-api.com
- Документация: https://doc.evolution-api.com
- GitHub: https://github.com/EvolutionAPI/evolution-api

---

**Итог: Evolution API можно использовать чисто кодом, n8n не нужен!** ✅


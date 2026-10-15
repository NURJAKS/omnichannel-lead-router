# 🚀 Быстрый запуск Evolution API

## ✅ Ответ на ваш вопрос: n8n НЕ нужен!

**Evolution API можно использовать:**
- ✅ **Чисто кодом** (REST API) - рекомендуемый способ
- ✅ **Через Python/Node.js** - напрямую
- ✅ **Через HTTP запросы** - curl, requests, axios

**n8n нужен только если:**
- Хотите визуальный редактор workflow
- Нужна автоматизация без кода
- Команда не программисты

**Для вашей CRM: используйте Evolution API напрямую через код!** 🎯

---

## 📦 Установка Evolution API

### **Вариант 1: Docker Compose (рекомендуется)**

```bash
cd /opt
mkdir -p evolution-api
cd evolution-api

# Создайте docker-compose.yml (скопируйте из проекта)
# Или используйте готовый файл из проекта

# Запустите
docker-compose -f /home/nurjaks/Development/crm/docker-compose.evolution.yml up -d
```

### **Вариант 2: Прямой Docker**

```bash
docker run -d \
  --name evolution-api \
  -p 8080:8080 \
  -e AUTHENTICATION_API_KEY=evolution-api-key-change-me \
  -e CONFIG_SESSION_PHONE_CLIENT=Chrome \
  -e CONFIG_SESSION_PHONE_NAME=CRM \
  -v /opt/evolution-api/instances:/evolution/instances \
  -v /opt/evolution-api/store:/evolution/store \
  atendai/evolution-api:latest
```

---

## ✅ Проверка работы

```bash
# Проверка здоровья
curl http://localhost:8080/health

# Должно вернуть:
# {"status":"ok"}
```

---

## 🔧 Интеграция с вашей CRM

### **1. Обновите .env:**

```env
# Evolution API
EVOLUTION_API_URL=http://localhost:8080
EVOLUTION_API_KEY=evolution-api-key-change-me
EVOLUTION_INSTANCE_NAME=crm-instance
```

### **2. Используйте в коде:**

```python
from evolution_integration import EvolutionAPIIntegration
from database import Database

db = Database()
evolution = EvolutionAPIIntegration(
    api_url="http://localhost:8080",
    api_key="evolution-api-key-change-me",
    instance_name="crm-instance",
    database=db
)

# Создать инстанс (один раз)
result = evolution.create_instance()
print(result)

# Получить QR код
qr = evolution.get_qr_code()
print(f"QR код: {qr}")

# Отправить сообщение
result = evolution.send_message("79991234567", "Привет из CRM!")
print(result)
```

---

## 📋 Пошаговая настройка

### **Шаг 1: Запустите Evolution API**

```bash
# Создайте директорию
sudo mkdir -p /opt/evolution-api
sudo chown $USER:$USER /opt/evolution-api
cd /opt/evolution-api

# Скопируйте docker-compose файл
cp /home/nurjaks/Development/crm/docker-compose.evolution.yml ./docker-compose.yml

# Запустите
docker-compose up -d

# Проверьте
curl http://localhost:8080/health
```

### **Шаг 2: Создайте инстанс**

```python
from evolution_integration import EvolutionAPIIntegration

evolution = EvolutionAPIIntegration(
    api_url="http://localhost:8080",
    api_key="evolution-api-key-change-me",
    instance_name="crm-instance"
)

# Создать
result = evolution.create_instance()
print(result)
```

### **Шаг 3: Получите QR код**

```python
qr = evolution.get_qr_code()
# Покажите QR код пользователю или сохраните
print(f"QR код: {qr}")
```

### **Шаг 4: Отсканируйте QR код**

1. Откройте WhatsApp на телефоне
2. Меню → "Связанные устройства"
3. Отсканируйте QR код

### **Шаг 5: Отправьте тестовое сообщение**

```python
result = evolution.send_message("79991234567", "Тест из CRM!")
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
| **Нужен n8n** | Нет | Нет ✅ |

---

## 💻 Использование чисто кодом (без n8n)

### **Примеры:**

```python
# Отправка сообщения
evolution.send_message("79991234567", "Привет!")

# Получение статуса
status = evolution.get_instance_status()

# Проверка здоровья
health = evolution.check_health()
```

### **Через HTTP (curl):**

```bash
# Отправить сообщение
curl -X POST http://localhost:8080/message/sendText/crm-instance \
  -H "apikey: evolution-api-key-change-me" \
  -H "Content-Type: application/json" \
  -d '{"number": "79991234567", "text": "Привет!"}'

# Получить статус
curl http://localhost:8080/instance/fetchInstances \
  -H "apikey: evolution-api-key-change-me"
```

---

## 🔗 Интеграция с web.py

```python
from evolution_integration import EvolutionAPIIntegration

# В web.py
evolution = EvolutionAPIIntegration(
    api_url=os.getenv("EVOLUTION_API_URL", "http://localhost:8080"),
    api_key=os.getenv("EVOLUTION_API_KEY"),
    instance_name=os.getenv("EVOLUTION_INSTANCE_NAME", "crm-instance"),
    database=db
)

# Роут для отправки
@app.post("/api/evolution/send")
async def send_evolution_message(request: Request):
    data = await request.json()
    result = evolution.send_message(data['phone'], data['message'])
    return JSONResponse(result)
```

---

## 🎉 Итог

**n8n НЕ нужен!** ✅

**Используйте Evolution API:**
- ✅ Чисто кодом (Python/Node.js)
- ✅ Через REST API
- ✅ Напрямую, без посредников

**Быстрее, стабильнее, проще!** 🚀


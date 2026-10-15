# 🧪 Пошаговая инструкция по тестированию Evolution API CRM

## ✅ Все сервисы запущены!

---

## 📋 ШАГ 1: Проверка Evolution API (1 минута)

### Проверьте, что Evolution API запущен:

```bash
# Проверка здоровья
curl http://localhost:8080/health

# Должно вернуть:
# {"status":"ok"}
```

### Если не запущен:

```bash
cd /opt/evolution-api
docker-compose up -d
sleep 5
curl http://localhost:8080/health
```

---

## 📋 ШАГ 2: Создание инстанса WhatsApp (2 минуты)

### Откройте Python консоль:

```bash
cd /home/nurjaks/Development/crm
source venv/bin/activate
python
```

### Выполните в Python:

```python
from evolution_integration import EvolutionAPIIntegration

# Создайте объект Evolution API
evolution = EvolutionAPIIntegration(
    api_url="http://localhost:8080",
    api_key="evolution-api-key-change-me",
    instance_name="crm-instance"
)

# Проверьте статус
status = evolution.check_health()
print("Health:", status)

# Проверьте существующие инстансы
instances = evolution.get_instance_status()
print("Instances:", instances)

# Создайте новый инстанс (если еще нет)
if instances.get("status") == "not_found":
    result = evolution.create_instance()
    print("Create result:", result)
else:
    print("Instance already exists:", instances)
```

### Что должно произойти:

- ✅ Health check вернет `{"status":"ok"}`
- ✅ Инстанс будет создан или уже существует
- ✅ Готово к подключению

---

## 📋 ШАГ 3: Получение QR кода (1 минута)

### В той же Python консоли:

```python
# Получите QR код
qr_data = evolution.get_qr_code()
print("QR Code:", qr_data)

# Если QR код в base64, сохраните его
if qr_data:
    import base64
    # Декодируйте и сохраните как изображение (опционально)
    # qr_image = base64.b64decode(qr_data)
    # with open('qr.png', 'wb') as f:
    #     f.write(qr_image)
```

### Или через API:

```bash
curl -X GET "http://localhost:8080/instance/connect/crm-instance" \
  -H "apikey: evolution-api-key-change-me"
```

---

## 📋 ШАГ 4: Подключение WhatsApp (2 минуты)

### 1. Откройте WhatsApp на телефоне

### 2. Меню (три точки) → "Связанные устройства"

### 3. Нажмите "Связать устройство"

### 4. Отсканируйте QR код

**Где взять QR код:**
- Из вывода Python команды выше
- Или через веб-интерфейс Evolution API (если настроен)
- Или через API запрос

### 5. Проверьте подключение:

```python
# В Python консоли
status = evolution.get_instance_status()
print("Status:", status)

# Должно показать:
# {"status": "open", "instanceName": "crm-instance", ...}
```

---

## 📋 ШАГ 5: Тест отправки сообщения (1 минута)

### В Python консоли:

```python
# Отправьте тестовое сообщение на свой номер
result = evolution.send_message("79991234567", "Привет из Evolution API CRM! 🚀")

print("Result:", result)

# Должно вернуть:
# {"key": {...}, "status": 200, ...}
```

### Проверьте телефон:

- ✅ Должно прийти сообщение "Привет из Evolution API CRM! 🚀"

---

## 📋 ШАГ 6: Тест получения сообщений (2 минуты)

### 1. Напишите боту в WhatsApp:

Отправьте сообщение на номер, который подключен к Evolution API

### 2. Проверьте логи:

```bash
# Логи Evolution API
docker logs evolution-api --tail 50

# Логи CRM
tail -f /home/nurjaks/Development/crm/crm.log 2>/dev/null || echo "Логи в терминале"
```

### 3. Проверьте базу данных:

```python
# В Python консоли
from database import Database
import asyncio

db = Database()
await db.init_db()

# Проверьте последние взаимодействия
import aiosqlite
async with aiosqlite.connect(db.db_path) as conn:
    async with conn.execute("""
        SELECT * FROM interactions 
        ORDER BY created_at DESC 
        LIMIT 5
    """) as cursor:
        rows = await cursor.fetchall()
        for row in rows:
            print(row)
```

---

## 📋 ШАГ 7: Интеграция с CRM (3 минуты)

### Обновите web.py для использования Evolution API:

```python
# В web.py добавьте:
from evolution_integration import EvolutionAPIIntegration
import os

# Инициализация Evolution API
evolution = EvolutionAPIIntegration(
    api_url=os.getenv("EVOLUTION_API_URL", "http://localhost:8080"),
    api_key=os.getenv("EVOLUTION_API_KEY", "evolution-api-key-change-me"),
    instance_name=os.getenv("EVOLUTION_INSTANCE_NAME", "crm-instance"),
    database=db
)

# Роут для отправки сообщений
@app.post("/api/evolution/send")
async def send_evolution_message(request: Request):
    data = await request.json()
    result = evolution.send_message(data['phone'], data['message'])
    return JSONResponse(result)

# Роут для статуса
@app.get("/api/evolution/status")
async def evolution_status():
    status = evolution.get_instance_status()
    health = evolution.check_health()
    return JSONResponse({
        "health": health,
        "instance": status
    })
```

### Перезапустите CRM:

```bash
pkill -f "python.*main.py"
cd /home/nurjaks/Development/crm
source venv/bin/activate
python main.py both
```

---

## 📋 ШАГ 8: Тест через веб-интерфейс (2 минуты)

### 1. Откройте веб-интерфейс:

```
http://localhost:8000
```

### 2. Проверьте статус Evolution API:

```bash
curl http://localhost:8000/api/evolution/status
```

### 3. Отправьте сообщение через API:

```bash
curl -X POST http://localhost:8000/api/evolution/send \
  -H "Content-Type: application/json" \
  -d '{"phone": "79991234567", "message": "Тест из веб-интерфейса!"}'
```

---

## 📋 ШАГ 9: Полный тест бота-менеджера (5 минут)

### 1. Напишите боту в WhatsApp: `Привет`

**Ожидаемый ответ:**
```
Добро пожаловать! 👋
Я ваш персональный менеджер. 
Для начала работы отправьте ваше имя:
```

### 2. Отправьте ваше имя: `Иван`

**Ожидаемый ответ:**
```
Отлично, Иван! 👋
Теперь отправьте ваш email (или 'пропустить'):
```

### 3. Отправьте email: `ivan@test.com`

**Ожидаемый ответ:**
```
Спасибо! Теперь отправьте название компании (или 'пропустить'):
```

### 4. Отправьте компанию: `ООО Тест`

**Ожидаемый ответ:**
```
✅ Регистрация завершена! Чем могу помочь?
```

### 5. Проверьте в CRM:

```bash
# Откройте веб-интерфейс
http://localhost:8000/clients

# Должен быть новый клиент "Иван"
```

---

## 📋 ШАГ 10: Тест команд бота (3 минуты)

### 1. Напишите: `Помощь`

**Ожидаемый ответ:**
```
📋 Доступные команды:

• Привет - начать диалог
• Статус - мои заказы и сделки
• Контакты - контактная информация
• Помощь - эта справка

Просто напишите ваш вопрос, и я помогу!
```

### 2. Напишите: `Статус`

**Ожидаемый ответ:**
```
📊 Ваши сделки:

• Заказ #123
  💰 10,000.00 ₽
  📊 Статус: in_progress
```

### 3. Напишите: `Контакты`

**Ожидаемый ответ:**
```
📞 Контактная информация:

Телефон: +7 (XXX) XXX-XX-XX
Email: info@example.com
...
```

---

## ✅ Чек-лист тестирования

- [ ] Evolution API запущен (`curl http://localhost:8080/health`)
- [ ] Инстанс создан
- [ ] QR код получен
- [ ] WhatsApp подключен
- [ ] Отправка сообщений работает
- [ ] Получение сообщений работает
- [ ] Регистрация клиента работает
- [ ] Команды бота работают
- [ ] Данные сохраняются в CRM
- [ ] Веб-интерфейс работает

---

## 🐛 Решение проблем

### Проблема: Evolution API не запускается

**Решение:**
```bash
# Проверьте Docker
docker ps -a | grep evolution

# Перезапустите
cd /opt/evolution-api
docker-compose restart

# Проверьте логи
docker logs evolution-api --tail 50
```

### Проблема: QR код не появляется

**Решение:**
```python
# Проверьте статус инстанса
status = evolution.get_instance_status()
print(status)

# Пересоздайте инстанс
evolution.create_instance()
qr = evolution.get_qr_code()
```

### Проблема: Сообщения не отправляются

**Решение:**
```python
# Проверьте статус
status = evolution.get_instance_status()
print("Status:", status)

# Должно быть: {"status": "open", ...}

# Проверьте формат номера
# Правильно: "79991234567" (без +, без пробелов)
```

### Проблема: Сообщения не приходят

**Решение:**
1. Проверьте, что webhook настроен
2. Проверьте логи Evolution API: `docker logs evolution-api`
3. Проверьте, что CRM получает webhook запросы

---

## 🎉 Готово!

Если все тесты прошли успешно, ваш Evolution API CRM работает правильно!

**Преимущества Evolution API:**
- ✅ Быстрый запуск (2-5 секунд)
- ✅ Стабильный (не требует браузера)
- ✅ REST API (легко интегрировать)
- ✅ Production ready

**n8n НЕ нужен - все работает чисто кодом!** 🚀



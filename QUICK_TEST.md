# ⚡ Быстрый запуск и тестирование - ПОШАГОВО

## 🚀 ШАГ 1: Установка и запуск Evolution API (5 минут)

### Выполните в терминале:

```bash
# 1. Создайте директорию (может потребоваться sudo)
sudo mkdir -p /opt/evolution-api
sudo chown $USER:$USER /opt/evolution-api
cd /opt/evolution-api

# 2. Скопируйте docker-compose файл
cp /home/nurjaks/Development/crm/docker-compose.evolution.yml ./docker-compose.yml

# 3. Запустите Evolution API
docker-compose up -d

# 4. Подождите 10 секунд и проверьте
sleep 10
curl http://localhost:8080/health

# Должно вернуть: {"status":"ok"}
```

---

## 🚀 ШАГ 2: Создание инстанса WhatsApp (2 минуты)

### Откройте Python:

```bash
cd /home/nurjaks/Development/crm
source venv/bin/activate
python
```

### Выполните в Python:

```python
from evolution_integration import EvolutionAPIIntegration

# Создайте объект
evolution = EvolutionAPIIntegration(
    api_url="http://localhost:8080",
    api_key="evolution-api-key-change-me",
    instance_name="crm-instance"
)

# Проверьте здоровье
print("Health:", evolution.check_health())

# Создайте инстанс
result = evolution.create_instance()
print("Create:", result)

# Получите QR код
qr = evolution.get_qr_code()
print("QR Code:", qr)
```

---

## 🚀 ШАГ 3: Подключение WhatsApp (1 минута)

1. **Откройте WhatsApp** на телефоне
2. **Меню** → **"Связанные устройства"**
3. **"Связать устройство"**
4. **Отсканируйте QR код** (из вывода Python выше)

---

## 🚀 ШАГ 4: Тест отправки сообщения (1 минута)

### В Python:

```python
# Отправьте сообщение на свой номер
result = evolution.send_message("79991234567", "Тест из Evolution API! 🚀")
print("Result:", result)
```

**Проверьте телефон** - должно прийти сообщение!

---

## 🚀 ШАГ 5: Тест получения сообщений (2 минуты)

1. **Напишите боту в WhatsApp:** `Привет`

2. **Проверьте логи:**
```bash
docker logs evolution-api --tail 20
```

3. **Проверьте базу данных:**
```python
# В Python
from database import Database
import aiosqlite

db = Database()
async with aiosqlite.connect(db.db_path) as conn:
    async with conn.execute("SELECT * FROM interactions ORDER BY created_at DESC LIMIT 5") as cursor:
        rows = await cursor.fetchall()
        for row in rows:
            print(row)
```

---

## 🚀 ШАГ 6: Полный тест бота (5 минут)

### Напишите боту в WhatsApp:

1. **`Привет`** → Бот попросит имя
2. **`Иван`** → Бот попросит email
3. **`ivan@test.com`** → Бот попросит компанию
4. **`ООО Тест`** → Регистрация завершена!

### Проверьте в веб-интерфейсе:

```
http://localhost:8000/clients
```

Должен быть новый клиент "Иван"!

---

## ✅ Проверка статуса

```bash
# Evolution API
curl http://localhost:8080/health

# Веб-интерфейс
curl http://localhost:8000/

# Статус инстанса
curl -X GET "http://localhost:8080/instance/fetchInstances" \
  -H "apikey: evolution-api-key-change-me"
```

---

## 🐛 Если что-то не работает

### Evolution API не запускается:
```bash
cd /opt/evolution-api
docker-compose logs
docker-compose restart
```

### QR код не появляется:
```python
# Пересоздайте инстанс
evolution.create_instance()
qr = evolution.get_qr_code()
```

### Сообщения не отправляются:
```python
# Проверьте статус
status = evolution.get_instance_status()
print(status)  # Должно быть {"status": "open"}
```

---

## 🎉 Готово!

Все работает? Отлично! 🚀

**Преимущества Evolution API:**
- ⚡ Быстрый запуск (2-5 секунд)
- ✅ Стабильный (без браузера)
- 💻 Чисто кодом (n8n не нужен!)



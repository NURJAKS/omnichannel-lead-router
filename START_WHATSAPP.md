# ⚡ БЫСТРЫЙ СТАРТ WhatsApp - 3 команды!

## 🚀 Вариант 1: Автоматический запуск (САМЫЙ БЫСТРЫЙ)

```bash
cd /home/nurjaks/Development/crm
./start_whatsapp.sh
```

**Готово!** Скрипт сам:
- ✅ Проверит зависимости
- ✅ Установит если нужно
- ✅ Запустит WhatsApp сервис
- ✅ Запустит CRM

---

## 🚀 Вариант 2: Ручной запуск (2 терминала)

### Терминал 1 - WhatsApp:
```bash
cd /home/nurjaks/Development/crm
node whatsapp_service.js
```

### Терминал 2 - CRM:
```bash
cd /home/nurjaks/Development/crm
source venv/bin/activate
python main.py both
```

---

## 📱 Подключение (1 раз):

1. **Откройте WhatsApp на телефоне**
2. **Меню** (три точки) → **"Связанные устройства"**
3. **"Связать устройство"**
4. **Отсканируйте QR код** из терминала
5. ✅ Готово!

---

## 🧪 Тест (30 секунд):

```bash
# Отправить тестовое сообщение
curl -X POST http://localhost:8000/api/whatsapp/send \
  -H "Content-Type: application/json" \
  -d '{"phone": "79991234567", "message": "Тест из CRM!"}'

# Проверить статус
curl http://localhost:8000/api/whatsapp/status
```

---

## ✅ Что работает:

- ✅ Клиенты пишут в WhatsApp → попадает в CRM
- ✅ Вы отвечаете через CRM → уходит в WhatsApp
- ✅ Все синхронизировано
- ✅ Работает с мобильными телефонами!

---

## 🎯 Использование в коде:

```python
from whatsapp_integration import WhatsAppIntegration
from database import Database

db = Database()
whatsapp = WhatsAppIntegration(database=db)

# Отправить сообщение клиенту
await whatsapp.send_client_notification(client_id, "Ваша сделка обновлена!")
```

---

## ⚠️ Важно:

1. **Телефон должен быть онлайн** - WhatsApp Web требует активное соединение
2. **Не делайте массовые рассылки** - максимум 20-30 сообщений/час
3. **Формат номера:** `79991234567` (без +, без пробелов)

---

## 🐛 Проблемы?

### QR код не появляется:
```bash
# Перезапустите WhatsApp сервис
pkill -f "whatsapp_service.js"
node whatsapp_service.js
```

### Сообщения не отправляются:
```bash
# Проверьте статус
curl http://localhost:3001/status
```

### Ошибка подключения:
- Убедитесь, что порт 3001 свободен
- Проверьте, что оба сервиса запущены

---

**Время установки: 3 минуты** ⚡


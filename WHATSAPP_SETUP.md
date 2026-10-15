# 🚀 Настройка бесплатного WhatsApp для CRM

## 📋 Что нужно

1. **Node.js** (версия 14+)
2. **Python** (уже установлен)
3. **Один телефон** с WhatsApp для подключения

## 🔧 Установка

### Шаг 1: Установка Node.js

```bash
# Проверьте, установлен ли Node.js
node --version

# Если нет, установите:
# Ubuntu/Debian:
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Или скачайте с nodejs.org
```

### Шаг 2: Установка зависимостей WhatsApp сервиса

```bash
cd /home/nurjaks/Development/crm
npm install whatsapp-web.js qrcode-terminal axios express
```

### Шаг 3: Настройка Python интеграции

```bash
# Установите requests если еще нет
pip install requests
```

### Шаг 4: Обновление requirements.txt

Добавьте в `requirements.txt`:
```
requests>=2.31.0
```

## 🚀 Запуск

### Вариант 1: Запуск всего вместе

**Терминал 1 - WhatsApp сервис:**
```bash
node whatsapp_service.js
```

**Терминал 2 - Python CRM:**
```bash
source venv/bin/activate
python main.py both
```

### Вариант 2: Только WhatsApp сервис

```bash
node whatsapp_service.js
```

## 📱 Первое подключение

1. Запустите `whatsapp_service.js`
2. Появится QR код в терминале
3. Откройте WhatsApp на телефоне
4. Нажмите меню (три точки) → "Связанные устройства"
5. Нажмите "Связать устройство"
6. Отсканируйте QR код
7. Готово! ✅

## 🧪 Тестирование

### Отправка сообщения из Python:

```python
from whatsapp_integration import WhatsAppIntegration

whatsapp = WhatsAppIntegration()
result = whatsapp.send_message("79991234567", "Привет из CRM!")
print(result)
```

### Проверка статуса:

```python
status = whatsapp.get_status()
print(status)
```

### Через API:

```bash
# Отправить сообщение
curl -X POST http://localhost:3001/send \
  -H "Content-Type: application/json" \
  -d '{"phone": "79991234567", "message": "Тест"}'

# Проверить статус
curl http://localhost:3001/status
```

## ⚙️ Конфигурация

Создайте `.env` и добавьте:

```env
# WhatsApp настройки
WHATSAPP_API_URL=http://localhost:3001
WHATSAPP_PORT=3001
CRM_API_URL=http://localhost:8000
```

## 🔄 Интеграция с текущей CRM

### Обновить web.py:

```python
from whatsapp_integration import WhatsAppIntegration, setup_whatsapp_routes

# После создания app
whatsapp = WhatsAppIntegration(database=db)
setup_whatsapp_routes(app, whatsapp)
```

### Отправка уведомлений клиентам:

```python
# В вашем коде, когда нужно отправить уведомление:
await whatsapp.send_client_notification(client_id, "Ваша сделка обновлена!")
```

## ⚠️ Важные моменты

1. **Телефон должен быть онлайн**
   - WhatsApp Web требует активное соединение
   - Если телефон выключен - перестанет работать

2. **Не делайте массовые рассылки**
   - WhatsApp может заблокировать за спам
   - Максимум 20-30 сообщений в час

3. **Один номер = один аккаунт**
   - Нельзя использовать один номер для множества ботов

4. **Риск блокировки**
   - Технически нарушает ToS WhatsApp
   - Но работает и многие используют
   - Для production лучше использовать официальный API

## 🎯 Что получится

✅ Клиенты пишут вам в WhatsApp на свои телефоны
✅ Вы получаете сообщения в CRM
✅ Вы можете отвечать через CRM
✅ Все синхронизировано в одной базе
✅ **Полностью бесплатно!**

## 🐛 Решение проблем

### QR код не появляется:
- Проверьте, что Node.js установлен
- Проверьте интернет соединение
- Перезапустите сервис

### Сообщения не отправляются:
- Проверьте, что телефон онлайн
- Проверьте формат номера (79991234567)
- Проверьте статус: `curl http://localhost:3001/status`

### Ошибка подключения:
- Убедитесь, что порт 3001 свободен
- Проверьте firewall
- Переподключите через QR код

## 📚 Дополнительно

- [whatsapp-web.js документация](https://github.com/pedroslopez/whatsapp-web.js)
- [Evolution API](https://evolution-api.com) - более стабильная альтернатива




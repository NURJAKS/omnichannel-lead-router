# ⚡ Быстрый запуск (оптимизировано)

## 🚀 Запуск (30 секунд)

### **1. WhatsApp сервис:**
```bash
cd /home/nurjaks/Development/crm
node whatsapp_service.js
```

**Что происходит:**
- ✅ HTTP API запускается **сразу** (порт 3001)
- ⏳ WhatsApp инициализируется в фоне (10-30 секунд)
- ✅ API доступен сразу, не ждет WhatsApp

**Проверка:**
```bash
# API доступен сразу
curl http://localhost:3001/health

# Статус WhatsApp (покажет "disconnected" пока не подключится)
curl http://localhost:3001/status
```

### **2. CRM:**
```bash
cd /home/nurjaks/Development/crm
source venv/bin/activate
python main.py both
```

**Что происходит:**
- ✅ Веб-интерфейс запускается (порт 8000)
- ✅ Telegram бот запускается
- ✅ Интеграция с WhatsApp готова

---

## ⏱️ Временные рамки

### **Первый запуск:**
- HTTP API: **мгновенно** ⚡
- WhatsApp подключение: **10-30 секунд** ⏳
- Веб-интерфейс: **5-10 секунд** ⏳

### **Повторный запуск (с сохраненной сессией):**
- HTTP API: **мгновенно** ⚡
- WhatsApp подключение: **5-10 секунд** ⚡
- Веб-интерфейс: **3-5 секунд** ⚡

---

## ✅ Проверка готовности

### **1. Проверка API (быстро):**
```bash
curl http://localhost:3001/health
# Должно вернуть: {"status":"ok","service":"whatsapp-api",...}
```

### **2. Проверка WhatsApp:**
```bash
curl http://localhost:3001/status
# Покажет "disconnected" пока не подключится
# После подключения: "connected"
```

### **3. Проверка веб-интерфейса:**
```bash
curl http://localhost:8000/
# Должен вернуть HTML
```

---

## 🐛 Если долго запускается

### **Проблема: WhatsApp не подключается**

**Решение:**
1. Проверьте, что QR код отсканирован
2. Проверьте интернет соединение
3. Перезапустите:
   ```bash
   pkill -f whatsapp_service
   node whatsapp_service.js
   ```

### **Проблема: Порты заняты**

**Решение:**
```bash
# Освободить порты
pkill -f whatsapp_service
pkill -f "python.*main.py"
pkill -f uvicorn

# Подождите 2 секунды
sleep 2

# Запустите заново
```

### **Проблема: Медленный первый запуск**

**Это нормально!** Первый запуск всегда медленнее:
- Puppeteer скачивает Chrome (если первый раз)
- WhatsApp Web инициализируется
- Повторные запуски будут быстрее

---

## 💡 Советы

1. **Используйте health checks:**
   ```bash
   curl http://localhost:3001/health
   ```
   API доступен сразу, не ждет WhatsApp

2. **Сохраняйте сессию:**
   После первого подключения сессия сохраняется
   Повторный запуск будет быстрее

3. **Запускайте в фоне:**
   ```bash
   nohup node whatsapp_service.js > whatsapp.log 2>&1 &
   nohup python main.py both > crm.log 2>&1 &
   ```

4. **Мониторинг:**
   ```bash
   # Следите за логами
   tail -f whatsapp.log
   tail -f crm.log
   ```

---

## 🎯 Итог

**API доступен сразу** - не ждите полной инициализации WhatsApp!

**Проверяйте готовность через health checks:**
```bash
curl http://localhost:3001/health  # API готов
curl http://localhost:3001/status  # WhatsApp статус
```

**Для production:** Используйте Evolution API (см. PRODUCTION_SOLUTIONS.md)


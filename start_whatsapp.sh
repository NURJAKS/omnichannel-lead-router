#!/bin/bash

# Скрипт для быстрого запуска WhatsApp интеграции

echo "🚀 Запуск WhatsApp CRM интеграции..."
echo ""

# Проверка Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js не установлен!"
    echo "Установите Node.js: https://nodejs.org"
    exit 1
fi

# Проверка зависимостей Node.js
if [ ! -d "node_modules" ]; then
    echo "📦 Установка зависимостей Node.js..."
    npm install
fi

# Проверка Python зависимостей
if [ ! -d "venv" ]; then
    echo "📦 Создание виртуального окружения Python..."
    python3 -m venv venv
fi

echo "✅ Все зависимости установлены!"
echo ""
echo "📱 Запуск WhatsApp сервиса..."
echo "   (Откройте WhatsApp на телефоне и отсканируйте QR код)"
echo ""

# Запуск WhatsApp сервиса в фоне
node whatsapp_service.js &
WHATSAPP_PID=$!

echo "✅ WhatsApp сервис запущен (PID: $WHATSAPP_PID)"
echo ""
echo "💡 Для остановки нажмите Ctrl+C или выполните: kill $WHATSAPP_PID"
echo ""

# Ждем немного для инициализации
sleep 2

echo "🌐 Запуск CRM с WhatsApp интеграцией..."
echo ""

# Активация venv и запуск CRM
source venv/bin/activate
python main.py both

# При остановке убиваем WhatsApp процесс
kill $WHATSAPP_PID 2>/dev/null


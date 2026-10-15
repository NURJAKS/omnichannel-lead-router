/**
 * WhatsApp сервис на Node.js с whatsapp-web.js
 * Работает с мобильными телефонами клиентов!
 * 
 * Установка:
 * npm install whatsapp-web.js qrcode-terminal axios
 * 
 * Запуск:
 * node whatsapp_service.js
 */

const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const axios = require('axios');

// Конфигурация
const CRM_API_URL = process.env.CRM_API_URL || 'http://localhost:8000';
const WHATSAPP_PORT = process.env.WHATSAPP_PORT || 3001;

// Создаем клиент WhatsApp
const client = new Client({
    authStrategy: new LocalAuth({
        dataPath: './whatsapp_session'
    }),
    puppeteer: {
        headless: true,
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',  // Экономит память
            '--disable-gpu',             // Ускоряет запуск
            '--no-first-run',
            '--disable-extensions',
            '--disable-background-timer-throttling',
            '--disable-backgrounding-occluded-windows',
            '--disable-renderer-backgrounding'
        ]
    }
});

// Генерация QR кода для подключения
client.on('qr', (qr) => {
    console.log('📱 Отсканируйте QR код в WhatsApp на вашем телефоне:');
    qrcode.generate(qr, { small: true });
    console.log('\nИли откройте: http://localhost:' + WHATSAPP_PORT + '/qr');
});

// Успешное подключение
client.on('ready', () => {
    console.log('✅ WhatsApp клиент готов!');
    console.log('📱 Теперь клиенты могут писать вам, и вы будете получать сообщения в CRM');
});

// Обработка входящих сообщений
client.on('message', async (message) => {
    // Пропускаем сообщения из групп (опционально)
    const chat = await message.getContact();
    
    // Пропускаем статусы и системные сообщения
    if (message.from === 'status@broadcast' || message.isStatus) {
        return;
    }
    
    const contact = await message.getContact();
    const chatInfo = await message.getChat();
    
    // Форматируем номер телефона
    const phoneNumber = contact.number.replace(/[^0-9]/g, '');
    
    // Информация о сообщении
    const messageData = {
        from: phoneNumber,
        fromName: contact.pushname || contact.name || 'Неизвестно',
        message: message.body,
        timestamp: new Date(message.timestamp * 1000).toISOString(),
        isGroup: chatInfo.isGroup,
        chatId: chatInfo.id._serialized
    };
    
    console.log('📨 Новое сообщение от:', messageData.fromName, '(', messageData.from, ')');
    console.log('💬 Текст:', messageData.message);
    
    // Отправляем в CRM через API
    try {
        const response = await axios.post(`${CRM_API_URL}/api/whatsapp/message`, messageData, {
            timeout: 5000
        });
        console.log('✅ Сообщение отправлено в CRM:', response.data);
    } catch (error) {
        console.error('❌ Ошибка отправки в CRM:', error.message);
        if (error.response) {
            console.error('Детали:', error.response.data);
        }
    }
});

// Обработка ошибок
client.on('auth_failure', (msg) => {
    console.error('❌ Ошибка аутентификации:', msg);
});

client.on('disconnected', (reason) => {
    console.log('⚠️ WhatsApp отключен:', reason);
    console.log('Переподключение...');
});

// Функция отправки сообщения
async function sendMessage(phone, message) {
    try {
        // Форматируем номер (убираем + и пробелы)
        const formattedPhone = phone.replace(/[^0-9]/g, '');
        const chatId = `${formattedPhone}@c.us`;
        
        await client.sendMessage(chatId, message);
        console.log(`✅ Сообщение отправлено на ${phone}`);
        return { success: true };
    } catch (error) {
        console.error(`❌ Ошибка отправки на ${phone}:`, error.message);
        return { success: false, error: error.message };
    }
}

// HTTP сервер для API (запускаем СРАЗУ, до инициализации WhatsApp)
const express = require('express');
const app = express();
app.use(express.json());

// Эндпоинт для отправки сообщений из CRM
app.post('/send', async (req, res) => {
    const { phone, message } = req.body;
    
    if (!phone || !message) {
        return res.status(400).json({ error: 'Нужны phone и message' });
    }
    
    // Проверяем, готов ли клиент
    if (!client.info) {
        return res.status(503).json({ 
            error: 'WhatsApp клиент еще не подключен',
            status: 'initializing'
        });
    }
    
    const result = await sendMessage(phone, message);
    res.json(result);
});

// Эндпоинт для получения статуса
app.get('/status', (req, res) => {
    res.json({
        status: client.info ? 'connected' : 'disconnected',
        info: client.info,
        ready: !!client.info
    });
});

// Эндпоинт для проверки здоровья (быстрый ответ)
app.get('/health', (req, res) => {
    res.json({ 
        status: 'ok', 
        service: 'whatsapp-api',
        whatsapp_ready: !!client.info
    });
});

// Запуск HTTP сервера СРАЗУ (не ждем WhatsApp)
app.listen(WHATSAPP_PORT, () => {
    console.log(`🌐 WhatsApp API сервер запущен на порту ${WHATSAPP_PORT}`);
    console.log(`📡 API: http://localhost:${WHATSAPP_PORT}/send`);
    console.log(`💚 Health check: http://localhost:${WHATSAPP_PORT}/health`);
    console.log(`⏳ Инициализация WhatsApp клиента... (это может занять 10-30 секунд)`);
});

// Инициализация WhatsApp клиента (асинхронно, не блокирует сервер)
console.log('🚀 Запуск WhatsApp сервиса...');
console.log('⏳ Инициализация браузера... (первый запуск может занять время)');

// Запускаем инициализацию
client.initialize().catch(err => {
    console.error('❌ Ошибка инициализации WhatsApp:', err);
});

// Экспорт для использования в других модулях
module.exports = { client, sendMessage };




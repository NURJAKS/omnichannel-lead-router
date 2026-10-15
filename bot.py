import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
from database import Database

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_USER_IDS", "").split(",") if x.strip()]

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменных окружения!")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
db = Database()


# Состояния для FSM
class ClientForm(StatesGroup):
    name = State()
    phone = State()
    email = State()
    company = State()
    notes = State()


class DealForm(StatesGroup):
    client_id = State()
    title = State()
    amount = State()
    status = State()
    description = State()


class TaskForm(StatesGroup):
    title = State()
    client_id = State()
    deal_id = State()
    description = State()
    due_date = State()


# Клавиатуры
def get_main_keyboard():
    """Главная клавиатура"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👥 Клиенты"), KeyboardButton(text="💼 Сделки")],
            [KeyboardButton(text="📋 Задачи"), KeyboardButton(text="📊 Статистика")],
            [KeyboardButton(text="🔍 Поиск")]
        ],
        resize_keyboard=True
    )
    return keyboard


def get_client_keyboard():
    """Клавиатура для работы с клиентами"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить клиента", callback_data="add_client")],
        [InlineKeyboardButton(text="📋 Список клиентов", callback_data="list_clients")],
        [InlineKeyboardButton(text="🔍 Поиск клиента", callback_data="search_client")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")]
    ])
    return keyboard


def get_deal_keyboard():
    """Клавиатура для работы со сделками"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить сделку", callback_data="add_deal")],
        [InlineKeyboardButton(text="📋 Все сделки", callback_data="list_deals")],
        [InlineKeyboardButton(text="🔄 По статусу", callback_data="deals_by_status")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")]
    ])
    return keyboard


def get_task_keyboard():
    """Клавиатура для работы с задачами"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить задачу", callback_data="add_task")],
        [InlineKeyboardButton(text="📋 Все задачи", callback_data="list_tasks")],
        [InlineKeyboardButton(text="⏰ Активные задачи", callback_data="pending_tasks")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")]
    ])
    return keyboard


# Команды
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    
    is_admin = user_id in ADMIN_IDS
    await db.add_user(user_id, username, first_name, last_name, is_admin)
    
    welcome_text = f"👋 Добро пожаловать в CRM систему, {first_name}!\n\n"
    welcome_text += "Используйте кнопки ниже для навигации:\n"
    welcome_text += "👥 Клиенты - управление клиентами\n"
    welcome_text += "💼 Сделки - управление сделками\n"
    welcome_text += "📋 Задачи - управление задачами\n"
    welcome_text += "📊 Статистика - общая статистика\n"
    welcome_text += "🔍 Поиск - поиск по базе"
    
    await message.answer(welcome_text, reply_markup=get_main_keyboard())


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    """Обработчик команды /help"""
    help_text = """
📖 **Справка по использованию CRM:**

**Основные команды:**
/start - Начать работу с ботом
/help - Показать эту справку
/stats - Быстрая статистика
/myid - Показать ваш Telegram ID

**Управление клиентами:**
- Добавление нового клиента
- Просмотр списка клиентов
- Поиск клиентов
- Редактирование данных

**Управление сделками:**
- Создание новых сделок
- Отслеживание статусов
- Фильтрация по статусам

**Управление задачами:**
- Создание задач
- Отслеживание дедлайнов
- Управление статусами

Используйте кнопки меню для удобной навигации!
    """
    await message.answer(help_text, parse_mode="Markdown")


@dp.message(Command("myid"))
async def cmd_myid(message: types.Message):
    """Показать ID пользователя"""
    user_id = message.from_user.id
    username = message.from_user.username or "не указан"
    first_name = message.from_user.first_name or "не указано"
    
    text = f"🆔 **Ваш Telegram ID:**\n\n"
    text += f"**ID:** `{user_id}`\n"
    text += f"**Username:** @{username}\n"
    text += f"**Имя:** {first_name}\n\n"
    text += f"💡 Скопируйте этот ID и добавьте в файл `.env`:\n"
    text += f"`ADMIN_USER_IDS={user_id}`\n\n"
    text += f"После этого перезапустите бота."
    
    await message.answer(text, parse_mode="Markdown")


@dp.message(Command("stats"))
async def cmd_stats(message: types.Message):
    """Быстрая статистика"""
    stats = await db.get_statistics()
    
    text = "📊 **Статистика CRM:**\n\n"
    text += f"👥 Клиентов: {stats['total_clients']}\n"
    text += f"💼 Сделок: {stats['total_deals']}\n"
    text += f"💰 Общая сумма: {stats['total_amount']:,.2f} ₽\n"
    text += f"📋 Активных задач: {stats['pending_tasks']}\n\n"
    
    if stats['deals_by_status']:
        text += "**Сделки по статусам:**\n"
        for status, data in stats['deals_by_status'].items():
            text += f"  • {status}: {data['count']} ({data['total']:,.2f} ₽)\n"
    
    await message.answer(text, parse_mode="Markdown")


# Обработчики кнопок главного меню
@dp.message(F.text == "👥 Клиенты")
async def clients_menu(message: types.Message):
    """Меню клиентов"""
    await message.answer("👥 **Управление клиентами**", 
                        reply_markup=get_client_keyboard(), 
                        parse_mode="Markdown")


@dp.message(F.text == "💼 Сделки")
async def deals_menu(message: types.Message):
    """Меню сделок"""
    await message.answer("💼 **Управление сделками**", 
                        reply_markup=get_deal_keyboard(), 
                        parse_mode="Markdown")


@dp.message(F.text == "📋 Задачи")
async def tasks_menu(message: types.Message):
    """Меню задач"""
    await message.answer("📋 **Управление задачами**", 
                        reply_markup=get_task_keyboard(), 
                        parse_mode="Markdown")


@dp.message(F.text == "📊 Статистика")
async def show_stats(message: types.Message):
    """Показать статистику"""
    await cmd_stats(message)


@dp.message(F.text == "🔍 Поиск")
async def search_menu(message: types.Message):
    """Меню поиска"""
    await message.answer("🔍 Введите поисковый запрос (имя, телефон, email или компания):")
    # Здесь можно добавить FSM для поиска


# Callback обработчики для клиентов
@dp.callback_query(F.data == "add_client")
async def add_client_start(callback: types.CallbackQuery, state: FSMContext):
    """Начать добавление клиента"""
    await callback.message.answer("Введите имя клиента:")
    await state.set_state(ClientForm.name)
    await callback.answer()


@dp.message(ClientForm.name)
async def process_client_name(message: types.Message, state: FSMContext):
    """Обработка имени клиента"""
    await state.update_data(name=message.text)
    await message.answer("Введите телефон (или /skip для пропуска):")
    await state.set_state(ClientForm.phone)


@dp.message(ClientForm.phone)
async def process_client_phone(message: types.Message, state: FSMContext):
    """Обработка телефона клиента"""
    if message.text != "/skip":
        await state.update_data(phone=message.text)
    await message.answer("Введите email (или /skip для пропуска):")
    await state.set_state(ClientForm.email)


@dp.message(ClientForm.email)
async def process_client_email(message: types.Message, state: FSMContext):
    """Обработка email клиента"""
    if message.text != "/skip":
        await state.update_data(email=message.text)
    await message.answer("Введите название компании (или /skip для пропуска):")
    await state.set_state(ClientForm.company)


@dp.message(ClientForm.company)
async def process_client_company(message: types.Message, state: FSMContext):
    """Обработка компании клиента"""
    if message.text != "/skip":
        await state.update_data(company=message.text)
    await message.answer("Введите заметки (или /skip для пропуска):")
    await state.set_state(ClientForm.notes)


@dp.message(ClientForm.notes)
async def process_client_notes(message: types.Message, state: FSMContext):
    """Обработка заметок и сохранение клиента"""
    data = await state.get_data()
    notes = message.text if message.text != "/skip" else None
    
    client_id = await db.add_client(
        name=data.get('name'),
        phone=data.get('phone'),
        email=data.get('email'),
        company=data.get('company'),
        notes=notes
    )
    
    await message.answer(f"✅ Клиент успешно добавлен! ID: {client_id}")
    await state.clear()


@dp.callback_query(F.data == "list_clients")
async def list_clients(callback: types.CallbackQuery):
    """Список всех клиентов"""
    clients = await db.get_all_clients()
    
    if not clients:
        await callback.message.answer("📭 Клиентов пока нет.")
        await callback.answer()
        return
    
    text = f"👥 **Список клиентов ({len(clients)}):**\n\n"
    for client in clients[:20]:  # Показываем первые 20
        text += f"**{client['id']}.** {client['name']}\n"
        if client['phone']:
            text += f"   📞 {client['phone']}\n"
        if client['email']:
            text += f"   📧 {client['email']}\n"
        if client['company']:
            text += f"   🏢 {client['company']}\n"
        text += "\n"
    
    if len(clients) > 20:
        text += f"\n... и еще {len(clients) - 20} клиентов"
    
    await callback.message.answer(text, parse_mode="Markdown")
    await callback.answer()


@dp.callback_query(F.data == "search_client")
async def search_client_start(callback: types.CallbackQuery):
    """Начать поиск клиента"""
    await callback.message.answer("🔍 Введите поисковый запрос:")
    await callback.answer()


@dp.callback_query(F.data == "list_deals")
async def list_deals(callback: types.CallbackQuery):
    """Список всех сделок"""
    deals = await db.get_all_deals()
    
    if not deals:
        await callback.message.answer("📭 Сделок пока нет.")
        await callback.answer()
        return
    
    text = f"💼 **Список сделок ({len(deals)}):**\n\n"
    for deal in deals[:20]:
        client = await db.get_client(deal['client_id'])
        client_name = client['name'] if client else f"ID: {deal['client_id']}"
        text += f"**#{deal['id']}** {deal['title']}\n"
        text += f"   👤 Клиент: {client_name}\n"
        text += f"   💰 Сумма: {deal['amount']:,.2f} ₽\n"
        text += f"   📊 Статус: {deal['status']}\n\n"
    
    if len(deals) > 20:
        text += f"\n... и еще {len(deals) - 20} сделок"
    
    await callback.message.answer(text, parse_mode="Markdown")
    await callback.answer()


@dp.callback_query(F.data == "list_tasks")
async def list_tasks(callback: types.CallbackQuery):
    """Список всех задач"""
    tasks = await db.get_all_tasks()
    
    if not tasks:
        await callback.message.answer("📭 Задач пока нет.")
        await callback.answer()
        return
    
    text = f"📋 **Список задач ({len(tasks)}):**\n\n"
    for task in tasks[:20]:
        text += f"**#{task['id']}** {task['title']}\n"
        text += f"   📊 Статус: {task['status']}\n"
        if task['due_date']:
            text += f"   ⏰ Дедлайн: {task['due_date']}\n"
        text += "\n"
    
    if len(tasks) > 20:
        text += f"\n... и еще {len(tasks) - 20} задач"
    
    await callback.message.answer(text, parse_mode="Markdown")
    await callback.answer()


@dp.callback_query(F.data == "pending_tasks")
async def pending_tasks(callback: types.CallbackQuery):
    """Активные задачи"""
    tasks = await db.get_all_tasks(status='pending')
    
    if not tasks:
        await callback.message.answer("✅ Нет активных задач!")
        await callback.answer()
        return
    
    text = f"⏰ **Активные задачи ({len(tasks)}):**\n\n"
    for task in tasks:
        text += f"**#{task['id']}** {task['title']}\n"
        if task['due_date']:
            text += f"   ⏰ Дедлайн: {task['due_date']}\n"
        text += "\n"
    
    await callback.message.answer(text, parse_mode="Markdown")
    await callback.answer()


@dp.callback_query(F.data == "main_menu")
async def back_to_main(callback: types.CallbackQuery):
    """Вернуться в главное меню"""
    await callback.message.answer("Главное меню", reply_markup=get_main_keyboard())
    await callback.answer()


# Обработка поисковых запросов
@dp.message(F.text)
async def handle_search(message: types.Message):
    """Обработка поисковых запросов"""
    query = message.text.strip()
    if len(query) < 2:
        return
    
    clients = await db.search_clients(query)
    
    if clients:
        text = f"🔍 **Найдено клиентов: {len(clients)}**\n\n"
        for client in clients[:10]:
            text += f"**{client['id']}.** {client['name']}\n"
            if client['phone']:
                text += f"   📞 {client['phone']}\n"
            if client['email']:
                text += f"   📧 {client['email']}\n"
            text += "\n"
        
        if len(clients) > 10:
            text += f"\n... и еще {len(clients) - 10} результатов"
        
        await message.answer(text, parse_mode="Markdown")
    else:
        await message.answer("❌ Ничего не найдено.")


async def main():
    """Главная функция запуска бота"""
    # Инициализация базы данных
    await db.init_db()
    print("✅ База данных инициализирована")
    
    # Запуск бота
    print("🚀 Бот запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())


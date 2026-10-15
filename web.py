from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os
from database import Database
from whatsapp_integration import WhatsAppBotManager, setup_whatsapp_routes
from google_sheets import GoogleSheetsSync, MockGoogleSheetsSync

app = FastAPI(title="CRM System")
templates = Jinja2Templates(directory="templates")
db = Database()

# Инициализация WhatsApp бота-менеджера
whatsapp = WhatsAppBotManager(database=db)
setup_whatsapp_routes(app, whatsapp)

# Инициализация Google Sheets (если настроено)
try:
    sheets = GoogleSheetsSync()
except:
    sheets = MockGoogleSheetsSync()


@app.on_event("startup")
async def startup():
    """Инициализация при запуске"""
    await db.init_db()
    print("✅ Web интерфейс запущен!")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Главная страница"""
    stats = await db.get_statistics()
    recent_clients = await db.get_all_clients()
    recent_deals = await db.get_all_deals()
    pending_tasks = await db.get_all_tasks(status='pending')
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "stats": stats,
        "recent_clients": recent_clients[:5],
        "recent_deals": recent_deals[:5],
        "pending_tasks": pending_tasks[:5]
    })


@app.get("/clients", response_class=HTMLResponse)
async def clients_page(request: Request):
    """Страница клиентов"""
    clients = await db.get_all_clients()
    return templates.TemplateResponse("clients.html", {
        "request": request,
        "clients": clients
    })


@app.post("/clients/add")
async def add_client(
    name: str = Form(...),
    phone: str = Form(None),
    email: str = Form(None),
    company: str = Form(None),
    notes: str = Form(None)
):
    """Добавить клиента"""
    await db.add_client(name, phone, email, company, notes)
    return RedirectResponse(url="/clients", status_code=303)


@app.get("/clients/{client_id}", response_class=HTMLResponse)
async def client_detail(request: Request, client_id: int):
    """Детали клиента"""
    client = await db.get_client(client_id)
    if not client:
        return RedirectResponse(url="/clients", status_code=303)
    
    deals = await db.get_deals_by_client(client_id)
    return templates.TemplateResponse("client_detail.html", {
        "request": request,
        "client": client,
        "deals": deals
    })


@app.get("/deals", response_class=HTMLResponse)
async def deals_page(request: Request, status: str = None):
    """Страница сделок"""
    deals = await db.get_all_deals(status=status)
    # Получаем информацию о клиентах для каждой сделки
    for deal in deals:
        client = await db.get_client(deal['client_id'])
        deal['client'] = client
    
    return templates.TemplateResponse("deals.html", {
        "request": request,
        "deals": deals,
        "current_status": status
    })


@app.post("/deals/add")
async def add_deal(
    client_id: int = Form(...),
    title: str = Form(...),
    amount: float = Form(0),
    status: str = Form("new"),
    description: str = Form(None)
):
    """Добавить сделку"""
    await db.add_deal(client_id, title, amount, status, description)
    return RedirectResponse(url=f"/clients/{client_id}", status_code=303)


@app.get("/tasks", response_class=HTMLResponse)
async def tasks_page(request: Request, status: str = None):
    """Страница задач"""
    tasks = await db.get_all_tasks(status=status)
    # Получаем информацию о клиентах и сделках
    for task in tasks:
        if task['client_id']:
            task['client'] = await db.get_client(task['client_id'])
        if task['deal_id']:
            task['deal'] = await db.get_deal(task['deal_id'])
    
    return templates.TemplateResponse("tasks.html", {
        "request": request,
        "tasks": tasks,
        "current_status": status
    })


@app.post("/tasks/add")
async def add_task(
    title: str = Form(...),
    client_id: int = Form(None),
    deal_id: int = Form(None),
    description: str = Form(None),
    due_date: str = Form(None)
):
    """Добавить задачу"""
    await db.add_task(title, client_id, deal_id, description, due_date)
    return RedirectResponse(url="/tasks", status_code=303)


@app.get("/stats", response_class=HTMLResponse)
async def stats_page(request: Request):
    """Страница статистики"""
    stats = await db.get_statistics()
    return templates.TemplateResponse("stats.html", {
        "request": request,
        "stats": stats
    })


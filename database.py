import aiosqlite
import os
from datetime import datetime
from typing import List, Optional, Dict, Any


class Database:
    def __init__(self, db_path: str = "crm.db"):
        self.db_path = db_path

    async def init_db(self):
        """Инициализация базы данных и создание таблиц"""
        async with aiosqlite.connect(self.db_path) as db:
            # Таблица клиентов
            await db.execute("""
                CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    phone TEXT,
                    email TEXT,
                    company TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Таблица сделок
            await db.execute("""
                CREATE TABLE IF NOT EXISTS deals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    amount REAL DEFAULT 0,
                    status TEXT DEFAULT 'new',
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (client_id) REFERENCES clients (id)
                )
            """)

            # Таблица задач
            await db.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id INTEGER,
                    deal_id INTEGER,
                    title TEXT NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'pending',
                    due_date TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (client_id) REFERENCES clients (id),
                    FOREIGN KEY (deal_id) REFERENCES deals (id)
                )
            """)

            # Таблица пользователей бота
            await db.execute("""
                CREATE TABLE IF NOT EXISTS bot_users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    is_admin INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Таблица истории взаимодействий (для WhatsApp и других каналов)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id INTEGER,
                    channel TEXT DEFAULT 'whatsapp',
                    message_type TEXT DEFAULT 'incoming',
                    message TEXT NOT NULL,
                    response TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (client_id) REFERENCES clients (id)
                )
            """)

            # Таблица для синхронизации с Google Sheets
            await db.execute("""
                CREATE TABLE IF NOT EXISTS sheets_sync (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    table_name TEXT NOT NULL,
                    record_id INTEGER NOT NULL,
                    sheet_row INTEGER,
                    synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(table_name, record_id)
                )
            """)

            await db.commit()

    # ========== CLIENT METHODS ==========
    async def add_client(self, name: str, phone: str = None, email: str = None, 
                        company: str = None, notes: str = None) -> int:
        """Добавить нового клиента"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO clients (name, phone, email, company, notes)
                VALUES (?, ?, ?, ?, ?)
            """, (name, phone, email, company, notes))
            await db.commit()
            return cursor.lastrowid

    async def get_client(self, client_id: int) -> Optional[Dict[str, Any]]:
        """Получить клиента по ID"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM clients WHERE id = ?", (client_id,)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    async def get_all_clients(self) -> List[Dict[str, Any]]:
        """Получить всех клиентов"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM clients ORDER BY created_at DESC") as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def search_clients(self, query: str) -> List[Dict[str, Any]]:
        """Поиск клиентов"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            search_term = f"%{query}%"
            async with db.execute("""
                SELECT * FROM clients 
                WHERE name LIKE ? OR phone LIKE ? OR email LIKE ? OR company LIKE ?
                ORDER BY created_at DESC
            """, (search_term, search_term, search_term, search_term)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def update_client(self, client_id: int, **kwargs) -> bool:
        """Обновить данные клиента"""
        valid_fields = ['name', 'phone', 'email', 'company', 'notes']
        updates = []
        values = []
        
        for field, value in kwargs.items():
            if field in valid_fields:
                updates.append(f"{field} = ?")
                values.append(value)
        
        if not updates:
            return False
        
        values.append(client_id)
        values.append(datetime.now())
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(f"""
                UPDATE clients 
                SET {', '.join(updates)}, updated_at = ?
                WHERE id = ?
            """, values)
            await db.commit()
            return True

    async def delete_client(self, client_id: int) -> bool:
        """Удалить клиента"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM clients WHERE id = ?", (client_id,))
            await db.commit()
            return True

    # ========== DEAL METHODS ==========
    async def add_deal(self, client_id: int, title: str, amount: float = 0, 
                      status: str = 'new', description: str = None) -> int:
        """Добавить новую сделку"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO deals (client_id, title, amount, status, description)
                VALUES (?, ?, ?, ?, ?)
            """, (client_id, title, amount, status, description))
            await db.commit()
            return cursor.lastrowid

    async def get_deal(self, deal_id: int) -> Optional[Dict[str, Any]]:
        """Получить сделку по ID"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM deals WHERE id = ?", (deal_id,)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    async def get_deals_by_client(self, client_id: int) -> List[Dict[str, Any]]:
        """Получить все сделки клиента"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM deals 
                WHERE client_id = ? 
                ORDER BY created_at DESC
            """, (client_id,)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def get_all_deals(self, status: str = None) -> List[Dict[str, Any]]:
        """Получить все сделки"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            if status:
                async with db.execute("""
                    SELECT * FROM deals 
                    WHERE status = ? 
                    ORDER BY created_at DESC
                """, (status,)) as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]
            else:
                async with db.execute("SELECT * FROM deals ORDER BY created_at DESC") as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]

    async def update_deal(self, deal_id: int, **kwargs) -> bool:
        """Обновить сделку"""
        valid_fields = ['title', 'amount', 'status', 'description']
        updates = []
        values = []
        
        for field, value in kwargs.items():
            if field in valid_fields:
                updates.append(f"{field} = ?")
                values.append(value)
        
        if not updates:
            return False
        
        values.append(deal_id)
        values.append(datetime.now())
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(f"""
                UPDATE deals 
                SET {', '.join(updates)}, updated_at = ?
                WHERE id = ?
            """, values)
            await db.commit()
            return True

    # ========== TASK METHODS ==========
    async def add_task(self, title: str, client_id: int = None, deal_id: int = None,
                      description: str = None, due_date: str = None) -> int:
        """Добавить новую задачу"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO tasks (title, client_id, deal_id, description, due_date)
                VALUES (?, ?, ?, ?, ?)
            """, (title, client_id, deal_id, description, due_date))
            await db.commit()
            return cursor.lastrowid

    async def get_task(self, task_id: int) -> Optional[Dict[str, Any]]:
        """Получить задачу по ID"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    async def get_all_tasks(self, status: str = None) -> List[Dict[str, Any]]:
        """Получить все задачи"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            if status:
                async with db.execute("""
                    SELECT * FROM tasks 
                    WHERE status = ? 
                    ORDER BY due_date ASC, created_at DESC
                """, (status,)) as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]
            else:
                async with db.execute("""
                    SELECT * FROM tasks 
                    ORDER BY due_date ASC, created_at DESC
                """) as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]

    async def update_task(self, task_id: int, **kwargs) -> bool:
        """Обновить задачу"""
        valid_fields = ['title', 'description', 'status', 'due_date']
        updates = []
        values = []
        
        for field, value in kwargs.items():
            if field in valid_fields:
                updates.append(f"{field} = ?")
                values.append(value)
        
        if not updates:
            return False
        
        values.append(task_id)
        values.append(datetime.now())
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(f"""
                UPDATE tasks 
                SET {', '.join(updates)}, updated_at = ?
                WHERE id = ?
            """, values)
            await db.commit()
            return True

    # ========== STATISTICS ==========
    async def get_statistics(self) -> Dict[str, Any]:
        """Получить статистику"""
        async with aiosqlite.connect(self.db_path) as db:
            # Количество клиентов
            async with db.execute("SELECT COUNT(*) FROM clients") as cursor:
                total_clients = (await cursor.fetchone())[0]

            # Количество сделок
            async with db.execute("SELECT COUNT(*) FROM deals") as cursor:
                total_deals = (await cursor.fetchone())[0]

            # Сумма всех сделок
            async with db.execute("SELECT SUM(amount) FROM deals") as cursor:
                total_amount = (await cursor.fetchone())[0] or 0

            # Сделки по статусам
            async with db.execute("""
                SELECT status, COUNT(*) as count, SUM(amount) as total
                FROM deals 
                GROUP BY status
            """) as cursor:
                deals_by_status = {row[0]: {'count': row[1], 'total': row[2] or 0} 
                                  for row in await cursor.fetchall()}

            # Активные задачи
            async with db.execute("""
                SELECT COUNT(*) FROM tasks WHERE status = 'pending'
            """) as cursor:
                pending_tasks = (await cursor.fetchone())[0]

            return {
                'total_clients': total_clients,
                'total_deals': total_deals,
                'total_amount': total_amount,
                'deals_by_status': deals_by_status,
                'pending_tasks': pending_tasks
            }

    # ========== USER METHODS ==========
    async def add_user(self, user_id: int, username: str = None, 
                      first_name: str = None, last_name: str = None, 
                      is_admin: bool = False):
        """Добавить пользователя бота"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO bot_users (user_id, username, first_name, last_name, is_admin)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, username, first_name, last_name, 1 if is_admin else 0))
            await db.commit()

    async def is_admin(self, user_id: int) -> bool:
        """Проверить, является ли пользователь администратором"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT is_admin FROM bot_users WHERE user_id = ?
            """, (user_id,)) as cursor:
                row = await cursor.fetchone()
                return bool(row[0]) if row else False


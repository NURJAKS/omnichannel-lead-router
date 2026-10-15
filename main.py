#!/usr/bin/env python3
"""
Главный файл для запуска CRM системы
Можно запустить только бота или только веб-интерфейс, или оба вместе
"""
import asyncio
import os
import sys
from dotenv import load_dotenv

load_dotenv()

def run_bot():
    """Запустить только Telegram бота"""
    from bot import main as bot_main
    asyncio.run(bot_main())


def run_web():
    """Запустить только веб-интерфейс"""
    import uvicorn
    from web import app
    uvicorn.run(app, host="0.0.0.0", port=8000)


def run_both():
    """Запустить и бота, и веб-интерфейс"""
    import uvicorn
    from web import app
    from bot import main as bot_main
    
    # Запускаем веб-интерфейс в отдельном потоке
    import threading
    web_thread = threading.Thread(
        target=lambda: uvicorn.run(app, host="0.0.0.0", port=8000),
        daemon=True
    )
    web_thread.start()
    
    # Запускаем бота в основном потоке
    asyncio.run(bot_main())


if __name__ == "__main__":
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        if mode == "bot":
            run_bot()
        elif mode == "web":
            run_web()
        elif mode == "both":
            run_both()
        else:
            print("Использование: python main.py [bot|web|both]")
            print("  bot  - запустить только Telegram бота")
            print("  web  - запустить только веб-интерфейс")
            print("  both - запустить и бота, и веб-интерфейс")
    else:
        # По умолчанию запускаем только бота
        print("Запуск Telegram бота...")
        print("Для запуска веб-интерфейса используйте: python main.py web")
        print("Для запуска обоих: python main.py both")
        run_bot()


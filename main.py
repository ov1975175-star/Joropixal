import sys
import os
sys.path.append(os.getcwd())

import asyncio
from aiogram import Bot, Dispatcher
from fastapi import FastAPI
import uvicorn
import threading
from bot.handlers.user import router as user_router
from bot.handlers.admin import router as admin_router

TOKEN = "8001535871:AAEr-DvtKgP3XggXNqih-rzy1Yfjx4UqAhI"
bot = Bot(token=TOKEN)
dp = Dispatcher()
app = FastAPI()

@app.get("/")
def health_check():
    return {"status": "Bot is active"}

dp.include_router(user_router)
dp.include_router(admin_router)

async def run_bot():
    await dp.start_polling(bot)

if __name__ == "__main__":
    threading.Thread(target=lambda: asyncio.run(run_bot())).start()
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
    

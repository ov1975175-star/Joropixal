import os
import asyncio
import logging
import threading

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from fastapi import FastAPI
import uvicorn

from bot.handlers import user, admin

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
app = FastAPI()

dp.include_router(user.router)
dp.include_router(admin.router)

@app.get("/")
def health_check():
    return {"status": "Active"}

async def start_bot():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_bot())

if __name__ == "__main__":
    t = threading.Thread(target=run_bot, daemon=True)
    t.start()
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
    

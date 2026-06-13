import os
import json
import asyncio
import threading
import logging

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
    return {"status": "Bot is Active ✅"}

async def run_bot():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    threading.Thread(target=lambda: asyncio.run(run_bot()), daemon=True).start()
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
    

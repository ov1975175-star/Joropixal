import os
import asyncio
import logging
import aiohttp
from contextlib import asynccontextmanager

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from fastapi import FastAPI
import uvicorn

from bot.handlers import user, admin

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
RENDER_URL = os.getenv("RENDER_URL", "https://joropixal.onrender.com")

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

dp.include_router(user.router)
dp.include_router(admin.router)

async def keep_alive():
    """Har 10 minute mein ping karo taaki service so na jaye"""
    await asyncio.sleep(60)
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                await session.get(RENDER_URL)
            logging.info("Keep-alive ping sent!")
        except Exception as e:
            logging.warning(f"Keep-alive failed: {e}")
        await asyncio.sleep(600)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await bot.delete_webhook(drop_pending_updates=True)
    polling_task = asyncio.create_task(
        dp.start_polling(bot, handle_signals=False)
    )
    keep_alive_task = asyncio.create_task(keep_alive())
    logging.info("Bot polling started!")
    
    yield
    
    # Shutdown
    polling_task.cancel()
    keep_alive_task.cancel()
    await bot.session.close()

app = FastAPI(lifespan=lifespan)

@app.get("/")
def health_check():
    return {"status": "Active"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8080)),
        log_level="info"
    )
    

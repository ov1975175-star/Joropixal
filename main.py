import os
import asyncio
import logging
import aiohttp

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from fastapi import FastAPI
import uvicorn

from bot.handlers import user, admin

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
RENDER_URL = os.getenv("RENDER_URL", "https://joropixal.onrender.com")

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
app = FastAPI()

dp.include_router(user.router)
dp.include_router(admin.router)

@app.get("/")
def health_check():
    return {"status": "Active"}

async def keep_alive():
    """Har 10 minute mein ping karo taaki service so na jaye"""
    await asyncio.sleep(60)  # pehle 1 min wait
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                await session.get(RENDER_URL)
            logging.info("Keep-alive ping sent!")
        except Exception as e:
            logging.warning(f"Keep-alive failed: {e}")
        await asyncio.sleep(600)  # 10 minute

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    
    bot_task = asyncio.create_task(
        dp.start_polling(bot, handle_signals=False)
    )
    
    keep_alive_task = asyncio.create_task(keep_alive())
    
    config = uvicorn.Config(app, host="0.0.0.0",
                           port=int(os.getenv("PORT", 10000)),
                           log_level="error")
    server = uvicorn.Server(config)
    server_task = asyncio.create_task(server.serve())
    
    await asyncio.gather(bot_task, server_task, keep_alive_task)

if __name__ == "__main__":
    asyncio.run(main())
    

import os
import asyncio
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
    return {"status": "Active"}

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Bot aur server dono ek saath chalao
    bot_task = asyncio.create_task(
        dp.start_polling(bot, handle_signals=False)
    )
    
    config = uvicorn.Config(app, host="0.0.0.0", 
                           port=int(os.getenv("PORT", 10000)),
                           log_level="error")
    server = uvicorn.Server(config)
    server_task = asyncio.create_task(server.serve())
    
    await asyncio.gather(bot_task, server_task)

if __name__ == "__main__":
    asyncio.run(main())
    

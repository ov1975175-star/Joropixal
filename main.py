import os
import asyncio
from aiogram import Bot, Dispatcher
from fastapi import FastAPI
import uvicorn
from bot.handlers import user, admin
import threading

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()
app = FastAPI()

@app.get("/")
def health_check(): return {"status": "Bot is active"}

dp.include_routers(user.router, admin.router)

async def run_polling(): await dp.start_polling(bot)

if __name__ == "__main__":
    threading.Thread(target=lambda: asyncio.run(run_polling())).start()
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
    

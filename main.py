import os
import asyncio
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher
from bot.handlers import user, admin

app = FastAPI()
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

dp.include_router(user.router)
dp.include_router(admin.router)

@app.post("/webhook")
async def handle_webhook(request: Request):
    update = await request.json()
    await dp.feed_raw_update(bot, update)
    return {"status": "ok"}

@app.on_event("startup")
async def on_startup():
    await bot.set_webhook(f"{WEBHOOK_URL}/webhook")
    

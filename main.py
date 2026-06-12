import os
import uvicorn
from fastapi import FastAPI
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from dotenv import load_dotenv

load_dotenv()

# YAHAN APNA NAYA TOKEN DALEIN
BOT_TOKEN = "8001535871:AAEr-DvtKgP3XggXNqih-rzy1Yfjx4UqAhI" 
WEBHOOK_URL = os.getenv("WEBHOOK_URL") 
WEBHOOK_PATH = "/webhook"

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher()
app = FastAPI()

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer("Bot live ho gaya hai!")

@app.on_event("startup")
async def on_startup():
    if WEBHOOK_URL:
        await bot.set_webhook(f"{WEBHOOK_URL.rstrip('/')}{WEBHOOK_PATH}")

@app.post(WEBHOOK_PATH)
async def bot_webhook(update: dict):
    telegram_update = types.Update(**update)
    await dp.feed_update(bot, telegram_update)
    return {"status": "ok"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
    

import os
import uvicorn
from fastapi import FastAPI
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv

# Environment variables load karein
load_dotenv()

# Variables fetch karein
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# Bot Setup (Fixed for Aiogram 3.7+)
bot = Bot(
    token=BOT_TOKEN, 
    default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
)
dp = Dispatcher()

# FastAPI app
app = FastAPI()

@app.on_event("startup")
async def on_startup():
    # Webhook set karna
    webhook_info = await bot.get_webhook_info()
    if webhook_info.url != f"{WEBHOOK_URL}/webhook":
        await bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")

@app.post("/webhook")
async def bot_webhook(update: dict):
    # Telegram update process karna
    telegram_update = types.Update(**update)
    await dp.feed_update(bot, telegram_update)
    return {"status": "ok"}

@app.get("/")
async def root():
    return {"status": "Bot is running perfectly"}

if __name__ == "__main__":
    # Render ke liye dynamic port
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
    

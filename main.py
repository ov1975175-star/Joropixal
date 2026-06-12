import asyncio
from aiogram import Bot, Dispatcher
from bot.handlers import user_router, admin_router

# Webhook URL (jo aapne Render ke Environment Variables mein set kiya hai)
WEBHOOK_URL = "https://joropixal.onrender.com" # Apna Render URL yahan daalein

async def main():
    bot = Bot(token="8001535871:AAEr-DvtKgP3XggXNqih-rzy1Yfjx4UqAhI")
    dp = Dispatcher()

    dp.include_router(user_router)
    dp.include_router(admin_router)

    # Webhook set karein
    await bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")
    print("Bot is running with Webhook...")
    
    # Yahan FastAPI ka server start karna hoga jo webhook requests receive kare
    # (Agar aapne FastAPI ka setup kiya hai toh)
    

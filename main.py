import asyncio
from aiogram import Bot, Dispatcher
from bot.handlers import user_router, admin_router
from fastapi import FastAPI
import uvicorn

bot = Bot(token="8001535871:AAEr-DvtKgP3XggXNqih-rzy1Yfjx4UqAhI")
dp = Dispatcher()
app = FastAPI()

dp.include_router(user_router)
dp.include_router(admin_router)

@app.post("/webhook")
async def handle_webhook(update: dict):
    # Webhook handling logic
    return {"status": "ok"}

if __name__ == "__main__":
    # Render par port 10000 use karein
    uvicorn.run(app, host="0.0.0.0", port=10000)
    

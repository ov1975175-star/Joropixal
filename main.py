import os
import uvicorn
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher
from bot.handlers import user, admin

app = FastAPI()
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

dp.include_router(user.router)
dp.include_router(admin.router)

@app.post("/webhook")
async def bot_webhook(request: Request):
    update = await request.json()
    await dp.feed_raw_update(bot, update)
    return {"status": "ok"}

@app.on_event("startup")
async def on_startup():
    await bot.set_webhook(f"{os.getenv('WEBHOOK_URL')}/webhook")

# Yeh line sabse zaroori hai Render ke liye
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=10000)
    

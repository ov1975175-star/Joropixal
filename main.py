import os
import uvicorn
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher
# Yahan direct file se import karein
from bot.handlers.user import router as user_router
from bot.handlers.admin import router as admin_router

app = FastAPI()
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

# Routers ko sirf yahan add karein
dp.include_router(user_router)
dp.include_router(admin.router)

@app.post("/webhook")
async def bot_webhook(request: Request):
    update = await request.json()
    await dp.feed_raw_update(bot, update)
    return {"status": "ok"}

@app.on_event("startup")
async def on_startup():
    await bot.set_webhook(f"{os.getenv('WEBHOOK_URL')}/webhook")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)
    

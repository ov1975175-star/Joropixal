import os
import json
import asyncio
import logging

from aiogram import Bot, Dispatcher
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

from bot.handlers import user, admin

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()
app = FastAPI()

dp.include_router(user.router)
dp.include_router(admin.router)

@app.get("/")
def health_check():
    return JSONResponse({"status": "Active"})

async def main():
    # Bot aur FastAPI dono ek saath chalao
    from uvicorn import Config, Server
    config = Config(app=app, host="0.0.0.0", 
                   port=int(os.getenv("PORT", 10000)), log_level="info")
    server = Server(config)
    
    await asyncio.gather(
        dp.start_polling(bot, skip_updates=True),
        server.serve()
    )

if __name__ == "__main__":
    asyncio.run(main())
    

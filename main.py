import os
import json  # ← ADD KARO
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from fastapi import FastAPI
import uvicorn
import threading
import firebase_admin
from firebase_admin import credentials, db

# --- SETUP ---
TOKEN = os.getenv("BOT_TOKEN")  # ← Hardcode mat karo

bot = Bot(token=TOKEN)
dp = Dispatcher()
app = FastAPI()

# --- FIREBASE ---
cred = credentials.Certificate(json.loads(os.getenv("FIREBASE_JSON")))
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://joro-gaming-default-rtdb.firebaseio.com'
})

# --- BOT LOGIC ---
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("Bot is online and working!")

# --- FASTAPI ---
@app.get("/")
def health_check():
    return {"status": "Active"}

async def run_bot():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    threading.Thread(target=lambda: asyncio.run(run_bot())).start()
    uvicorn.run(app, host="0.0.0.0", 
                port=int(os.getenv("PORT", 10000)))

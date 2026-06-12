from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

# Yahan 'router' define hona bahut zaroori hai
router = Router()

# Ab aap is router ka use karke handlers banayein
@router.message(Command("start"))
async def start_handler(message: Message):
    await message.answer("Hello!")
    

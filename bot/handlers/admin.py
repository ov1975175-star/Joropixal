from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()  # Ye line hona zaroori hai

@router.message(Command("start"))
async def start_handler(message: Message):
    await message.answer("Hello! Bot is online.")
    

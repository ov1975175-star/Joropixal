from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart

router = Router()

@router.message(CommandStart())
async def start_cmd(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛍 Products", callback_data="products")],
        [InlineKeyboardButton(text="📦 My Purchases", callback_data="purchases"), InlineKeyboardButton(text="💬 Support", callback_data="support")],
        [InlineKeyboardButton(text="⚙ Admin Panel", callback_data="admin_panel")]
    ])
    await message.answer("👋 Welcome, Joro pixel!\n\n👇 What would you like to do?", reply_markup=kb)
  

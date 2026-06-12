from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from FirebaseService import FirebaseService

router = Router()
firebase = FirebaseService()

def get_main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Products", callback_data="menu:products")],
        [InlineKeyboardButton(text="📦 My Purchases", callback_data="menu:purchases")],
        [InlineKeyboardButton(text="💬 Support", callback_data="menu:support"), 
         InlineKeyboardButton(text="👤 Profile", callback_data="menu:profile")]
    ])

@router.message(F.text == "/start")
async def start_handler(message: Message):
    await message.answer("👋 Welcome to Joro Pixel!\n\nWhat would you like to do?", reply_markup=get_main_menu())

@router.callback_query(F.data == "menu:products")
async def show_products(call: CallbackQuery):
    await call.message.edit_text("🛒 Available Products:\n\n(No products found in DB)", reply_markup=get_main_menu())
    

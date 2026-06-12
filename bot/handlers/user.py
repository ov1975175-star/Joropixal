from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from FirebaseService import FirebaseService

router = Router()
firebase = FirebaseService()

# Main Menu ka design
def get_main_menu():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Products", callback_data="menu:products")],
        [InlineKeyboardButton(text="📦 My Purchases", callback_data="menu:purchases")],
        [InlineKeyboardButton(text="💬 Support", callback_data="menu:support"), 
         InlineKeyboardButton(text="👤 Profile", callback_data="menu:profile")]
    ])
    return keyboard

@router.message(F.text == "/start")
async def start_handler(message: Message):
    await message.answer("👋 Welcome to Digital Store!\n\nChoose an option below:", reply_markup=get_main_menu())

@router.callback_query(F.data == "menu:products")
async def show_products(call: CallbackQuery):
    # Yahan Firebase se data fetch karo
    await call.message.edit_text("🛒 Available Products:\n\n(Yahan database se products aayenge)", reply_markup=get_main_menu())
    

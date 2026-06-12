from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

@router.callback_query(F.data == "admin_panel")
async def admin_panel(call: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📦 Products", callback_data="admin_products"), InlineKeyboardButton(text="📢 Broadcast", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="⬅ Back", callback_data="back_main")]
    ])
    await call.message.edit_text("⚙ **Admin Panel - Pixel to app bot**\n\nStats: 0 users, 0 sales.", reply_markup=kb)
    
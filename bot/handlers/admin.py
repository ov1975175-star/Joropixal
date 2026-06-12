from aiogram import Router, F
from aiogram.types import CallbackQuery

router = Router()

@router.callback_query(F.data == "admin_panel")
async def admin_panel(call: CallbackQuery):
    await call.message.edit_text(
        "⚙ **Admin Panel**\n\nAbhi yahan koi stats nahi hain. Product add karne ke liye database setup complete karein.",
        parse_mode="Markdown"
    )
  

from aiogram import Router, F
from aiogram.types import CallbackQuery
from FirebaseService import FirebaseService

router = Router()
db = FirebaseService()

# Admin verification ka button
@router.callback_query(F.data.startswith("verify:"))
async def approve(call: CallbackQuery):
    order_id = call.data.split(":")[1]
    # Firebase mein status update karo
    db.update_order(order_id, {"status": "approved"})
    await call.message.edit_text("✅ Order Approved!")
    await call.bot.send_message(call.from_user.id, "✅ Payment Verified! Product mil gaya.")
    

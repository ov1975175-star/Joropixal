from aiogram import Router, F
from aiogram.types import CallbackQuery
from FirebaseService import FirebaseService

router = Router()
db = FirebaseService()

@router.callback_query(F.data.startswith("verify:"))
async def verify_payment(call: CallbackQuery):
    order_id = call.data.split(":")[1]
    # Firebase mein status 'approved' karo
    db.update_order(order_id, {"status": "approved"})
    
    # User ko file bhejo
    order_data = db.get_order(order_id)
    await call.bot.send_message(order_data['user_id'], "✅ Payment Verified! Ye raha aapka product: " + order_data['product_link'])
    await call.message.edit_text("✅ Order Verified Successfully.")
    

from aiogram import Router, F
from aiogram.types import CallbackQuery
from FirebaseService import FirebaseService

router = Router()
firebase = FirebaseService()
ADMIN_ID = "5334467000" # Yahan apni Telegram Admin ID daalein

@router.callback_query(F.data.startswith("verify_payment:"))
async def handle_verify_payment(call: CallbackQuery):
    order_id = call.data.split(":")[1]
    user_id = str(call.from_user.id)
    
    order = firebase.get_order(order_id)
    
    if not order or order.get('user_id') != user_id:
        await call.answer("❌ Invalid order.", show_alert=True)
        return
    if order.get('status') != 'pending':
        await call.answer("⚠️ Order already processed.", show_alert=True)
        return

    firebase.update_order(order_id, {'status': 'pending_verification'})

    await call.bot.send_message(ADMIN_ID, f"🔔 <b>New Payment Verification!</b>\nOrder: <code>{order_id}</code>")

    await call.message.edit_text(
        f"⏳ <b>Verification submitted!</b>\n\n"
        f"Team check kar rahi hai, status update mil jayega.\n\n"
        f"🧾 Order ID: <code>{order_id}</code>"
    )
    

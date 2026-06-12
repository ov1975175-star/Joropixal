from aiogram import F
from aiogram.types import CallbackQuery

# Assuming aapne 'firebase' aur 'notif' object setup kar rakhe hain
@router.callback_query(F.data.startswith("verify_payment:"))
async def handle_verify_payment(call: CallbackQuery):
    order_id = call.data.split(":")[1]
    user_id = str(call.from_user.id)
    
    # 1. Firebase se order fetch karein
    order = firebase.get_order(order_id)
    
    # 2. Validation
    if not order or order['user_id'] != user_id:
        await call.answer("❌ Invalid order.", show_alert=True)
        return
    if order['status'] != 'pending':
        await call.answer("⚠️ Order already processed.", show_alert=True)
        return

    # 3. Status update
    firebase.update_order(order_id, {'status': 'pending_verification'})

    # 4. Admin ko notify karein
    await bot.send_message(ADMIN_ID, f"🔔 <b>New Payment Verification!</b>\nOrder: <code>{order_id}</code>")

    # 5. User ko confirm karein
    await call.message.edit_text(
        f"⏳ <b>Verification submitted!</b>\n\n"
        f"Team check kar rahi hai, status update mil jayega.\n\n"
        f"🧾 Order ID: <code>{order_id}</code>"
    )
    

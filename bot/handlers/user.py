@router.callback_query(F.data.startswith("buy:"))
async def process_buy(call: CallbackQuery):
    product_id = call.data.split(":")[1]
    product = db.get_product(product_id) # Product details fetch karo
    
    # Firebase mein Order save karo
    order_id = "ord_" + str(call.from_user.id)
    db.save_order(order_id, {"user_id": call.from_user.id, "status": "pending"})
    
    # Admin ka QR show karo
    await call.message.answer(f"💰 Price: {product['price']}\n\nIs QR par payment karein aur screenshot bhejein:", 
                               reply_markup=get_qr_keyboard(product['qr_link']))
    

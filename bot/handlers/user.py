@router.callback_query(F.data.startswith("buy:"))
async def order(call: CallbackQuery):
    # User ko QR bhejo aur order pending karo
    await call.message.answer("Pay here: [QR Link]\nScreenshot bhejo!")
    # Database mein pending order save karo
    

@router.callback_query(F.data.startswith("product:"))
async def show_product_detail(call: CallbackQuery):
    product_id = call.data.split(":")[1]
    product = db.get_product(product_id)
    if not product:
        await call.answer("Product not found!", show_alert=True)
        return

    is_free = int(product.get('price', 1)) == 0

    text = (
        f"📦 <b>{product['name']}</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"💰 Price: <b>{'FREE 🎁' if is_free else '₹' + str(product['price'])}</b>\n\n"
        f"📝 <b>Description:</b>\n"
        f"{product.get('description', 'Premium quality product.')}\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"{'✅ Click below to get instantly!' if is_free else '✅ Instant delivery after payment verification'}"
    )

    if is_free:
        buttons = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🎁 Get Free — Click Here", callback_data=f"getfree:{product_id}")],
            [InlineKeyboardButton(text="◀️ Back to Products", callback_data="show_products")]
        ])
    else:
        buttons = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💳 Buy Now — ₹" + str(product['price']), callback_data=f"buy:{product_id}")],
            [InlineKeyboardButton(text="◀️ Back to Products", callback_data="show_products")]
        ])

    if product.get('photo_url'):
        try:
            await call.message.answer_photo(
                photo=product['photo_url'],
                caption=text,
                reply_markup=buttons,
                parse_mode="HTML"
            )
            await call.message.delete()
            await call.answer()
            return
        except:
            pass

    try:
        await call.message.edit_text(text, reply_markup=buttons, parse_mode="HTML")
    except:
        await call.message.answer(text, reply_markup=buttons, parse_mode="HTML")


@router.callback_query(F.data.startswith("getfree:"))
async def get_free_product(call: CallbackQuery):
    product_id = call.data.split(":")[1]
    product = db.get_product(product_id)
    if not product:
        await call.answer("Product not found!", show_alert=True)
        return

    file_link = product.get('product_file')
    if not file_link:
        await call.answer("File not available yet!", show_alert=True)
        return

    # Order save karo free me
    db.create_order(
        user_id=call.from_user.id,
        username=call.from_user.username or call.from_user.full_name,
        product_id=product_id,
        product_name=product['name'],
        price=0
    )

    await call.message.answer(
        f"🎁 <b>Your Free Product!</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"📦 <b>{product['name']}</b>\n\n"
        f"🔗 <b>Download Link:</b>\n{file_link}\n\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"Enjoy! 🙏",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Home", callback_data="go_home")]
        ]),
        parse_mode="HTML"
    )
    await call.answer("Here's your free product! 🎁")

import os
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from FirebaseService import FirebaseService

router = Router()
db = FirebaseService()

ADMIN_IDS_RAW = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = []
for x in ADMIN_IDS_RAW.split(","):
    x = x.strip()
    if x.isdigit():
        ADMIN_IDS.append(int(x))

def get_bot():
    return Bot(token=os.getenv("BOT_TOKEN"))

def is_admin(user_id):
    return user_id in ADMIN_IDS

class AddProduct(StatesGroup):
    name = State()
    price = State()
    description = State()
    photo_url = State()
    qr_url = State()

def admin_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📦 Products", callback_data="admin_products"),
            InlineKeyboardButton(text="👥 Users", callback_data="admin_users")
        ],
        [
            InlineKeyboardButton(text="🕐 Pending Orders", callback_data="admin_pending"),
            InlineKeyboardButton(text="📊 Stats", callback_data="admin_stats")
        ],
        [InlineKeyboardButton(text="🏠 Home", callback_data="go_home")]
    ])


@router.callback_query(F.data == "admin_panel")
async def admin_panel(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("❌ Access Denied!", show_alert=True)
        return

    users = db.get_all_users()
    orders = db.get_pending_orders()
    products = db.get_all_products()

    await call.message.edit_text(
        f"⚙️ <b>Admin Control Panel</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"👥 Total Users: <b>{len(users)}</b>\n"
        f"📦 Products: <b>{len(products)}</b>\n"
        f"🕐 Pending Orders: <b>{len(orders)}</b>\n"
        f"━━━━━━━━━━━━━━━━",
        reply_markup=admin_menu(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "admin_products")
async def admin_products(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return

    products = db.get_all_products()
    buttons = []
    for p in products:
        status = "✅" if p.get('active', True) else "❌"
        buttons.append([
            InlineKeyboardButton(
                text=f"{status} {p['name']} — ₹{p['price']}",
                callback_data=f"admin_product_detail:{p['id']}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="➕ Add New Product", callback_data="add_product")])
    buttons.append([InlineKeyboardButton(text="◀️ Back", callback_data="admin_panel")])

    await call.message.edit_text(
        f"📦 <b>Products ({len(products)})</b>\n━━━━━━━━━━━━━━━━",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("admin_product_detail:"))
async def admin_product_detail(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return

    product_id = call.data.split(":")[1]
    product = db.get_product(product_id)
    if not product:
        await call.answer("Product not found!", show_alert=True)
        return

    status = "✅ Active" if product.get('active', True) else "❌ Inactive"
    text = (
        f"📦 <b>{product['name']}</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"💰 Price: ₹{product['price']}\n"
        f"📝 {product.get('description', 'No description')}\n"
        f"🖼️ Photo: {'✅' if product.get('photo_url') else '❌'}\n"
        f"📲 QR: {'✅' if product.get('qr_url') else '❌'}\n"
        f"Status: {status}"
    )

    toggle_text = "❌ Deactivate" if product.get('active', True) else "✅ Activate"
    buttons = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=toggle_text, callback_data=f"toggle_product:{product_id}")],
        [InlineKeyboardButton(text="🗑️ Delete Product", callback_data=f"del_product:{product_id}")],
        [InlineKeyboardButton(text="◀️ Back", callback_data="admin_products")]
    ])

    await call.message.edit_text(text, reply_markup=buttons, parse_mode="HTML")


@router.callback_query(F.data.startswith("toggle_product:"))
async def toggle_product(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return
    product_id = call.data.split(":")[1]
    product = db.get_product(product_id)
    new_status = not product.get('active', True)
    db.update_product(product_id, {"active": new_status})
    status = "✅ Activated" if new_status else "❌ Deactivated"
    await call.answer(f"Product {status}!", show_alert=True)
    await admin_product_detail(call)


@router.callback_query(F.data == "add_product")
async def add_product_start(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        return
    await call.message.answer(
        "📦 <b>Add New Product</b>\n\nEnter product <b>name</b>:",
        parse_mode="HTML"
    )
    await state.set_state(AddProduct.name)
    await call.answer()


@router.message(AddProduct.name)
async def add_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("💰 Enter <b>price</b> (numbers only, e.g. 99):", parse_mode="HTML")
    await state.set_state(AddProduct.price)


@router.message(AddProduct.price)
async def add_price(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Numbers only! Try again:")
        return
    await state.update_data(price=int(message.text))
    await message.answer("📝 Enter product <b>description</b>:", parse_mode="HTML")
    await state.set_state(AddProduct.description)


@router.message(AddProduct.description)
async def add_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer(
        "🖼️ Send <b>product photo URL</b>\n\n"
        "(Upload to imgbb.com → get direct link)\n"
        "Or type <b>skip</b>:",
        parse_mode="HTML"
    )
    await state.set_state(AddProduct.photo_url)


@router.message(AddProduct.photo_url)
async def add_photo(message: Message, state: FSMContext):
    photo_url = "" if message.text.lower() == "skip" else message.text
    await state.update_data(photo_url=photo_url)
    await message.answer(
        "📲 Send <b>QR code image URL</b>\n\n"
        "(Upload QR to imgbb.com → get direct link)\n"
        "Or type <b>skip</b>:",
        parse_mode="HTML"
    )
    await state.set_state(AddProduct.qr_url)


@router.message(AddProduct.qr_url)
async def add_qr(message: Message, state: FSMContext):
    qr_url = "" if message.text.lower() == "skip" else message.text
    data = await state.get_data()

    product_id = db.add_product(
        name=data['name'],
        price=data['price'],
        description=data['description'],
        photo_url=data.get('photo_url', ''),
        qr_url=qr_url
    )
    await state.clear()
    await message.answer(
        f"✅ <b>Product Added!</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"📦 {data['name']}\n"
        f"💰 ₹{data['price']}\n"
        f"🖼️ Photo: {'✅' if data.get('photo_url') else '❌'}\n"
        f"📲 QR: {'✅' if qr_url else '❌'}",
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("del_product:"))
async def delete_product(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return
    product_id = call.data.split(":")[1]
    db.delete_product(product_id)
    await call.answer("🗑️ Product deleted!", show_alert=True)
    await admin_products(call)


@router.callback_query(F.data == "admin_pending")
async def admin_pending(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return

    orders = db.get_pending_orders()
    if not orders:
        await call.answer("No pending orders!", show_alert=True)
        return

    await call.message.edit_text(
        f"🕐 <b>Pending Orders ({len(orders)})</b>\n━━━━━━━━━━━━━━━━\n\nSending details...",
        parse_mode="HTML"
    )

    for o in orders:
        await call.message.answer(
            f"🕐 <b>Pending Order</b>\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"👤 @{o.get('username','N/A')}\n"
            f"📦 {o['product_name']} — ₹{o['price']}\n"
            f"🔖 <code>{o['id'][:8]}</code>",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="✅ Approve", callback_data=f"approve:{o['id']}:{o['user_id']}"),
                    InlineKeyboardButton(text="❌ Reject", callback_data=f"reject:{o['id']}:{o['user_id']}")
                ]
            ]),
            parse_mode="HTML"
        )
    await call.answer()


@router.callback_query(F.data.startswith("approve:"))
async def approve_order(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return

    parts = call.data.split(":")
    order_id = parts[1]
    user_id = parts[2]
    order = db.get_order(order_id)
    db.update_order(order_id, {"status": "approved"})

    # Product details fetch karo
    product_id = order.get('product_id')
    product = db.get_product(product_id) if product_id else None

    bot = get_bot()
    try:
        # Step 1: Approval message
        await bot.send_message(
            int(user_id),
            f"🎉 <b>Payment Approved!</b>\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"✅ <b>{order['product_name']}</b> ka order confirm ho gaya!\n\n"
            f"📦 Neeche aapka product hai:",
            parse_mode="HTML"
        )

        # Step 2: Product photo bhejo (agar hai)
        if product and product.get('photo_url'):
            try:
                await bot.send_photo(
                    int(user_id),
                    photo=product['photo_url'],
                    caption=f"🖼️ <b>{product['name']}</b>",
                    parse_mode="HTML"
                )
            except:
                pass

        # Step 3: Product details bhejo
        if product:
            await bot.send_message(
                int(user_id),
                f"📦 <b>Product Details</b>\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"🏷️ Name: <b>{product['name']}</b>\n"
                f"💰 Price: ₹{product['price']}\n"
                f"📝 {product.get('description', '')}\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"🙏 Thank you for your purchase!",
                parse_mode="HTML"
            )

        # Step 4: QR code bhejo (agar hai)
        if product and product.get('qr_url'):
            try:
                await bot.send_photo(
                    int(user_id),
                    photo=product['qr_url'],
                    caption="📲 <b>Your QR Code</b>",
                    parse_mode="HTML"
                )
            except:
                pass

    except Exception as e:
        pass
    await bot.session.close()

    await call.message.edit_text(
        call.message.text + "\n\n✅ <b>APPROVED & PRODUCT SENT TO USER</b>",
        parse_mode="HTML"
    )
    await call.answer("✅ Approved & Product Sent!")


@router.callback_query(F.data.startswith("reject:"))
async def reject_order(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return

    parts = call.data.split(":")
    order_id = parts[1]
    user_id = parts[2]
    db.update_order(order_id, {"status": "rejected"})

    bot = get_bot()
    try:
        await bot.send_message(
            int(user_id),
            f"❌ <b>Payment Rejected</b>\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"Sorry, your payment could not be verified.\n\n"
            f"Please contact support if you believe this is an error.",
            parse_mode="HTML"
        )
    except:
        pass
    await bot.session.close()

    await call.message.edit_text(
        call.message.text + "\n\n❌ <b>REJECTED & USER NOTIFIED</b>",
        parse_mode="HTML"
    )
    await call.answer("❌ Rejected!")


@router.callback_query(F.data == "admin_users")
async def admin_users(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return

    users = db.get_all_users()
    text = f"👥 <b>Total Users: {len(users)}</b>\n━━━━━━━━━━━━━━━━\n\n"
    for u in users[:25]:
        text += f"• @{u.get('username','N/A')} — {u.get('full_name','')}\n"
    if len(users) > 25:
        text += f"\n...and {len(users)-25} more"

    await call.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Back", callback_data="admin_panel")]
        ]),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "admin_stats")
async def admin_stats(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return

    users = db.get_all_users()
    products = db.get_all_products()
    pending = db.get_pending_orders()

    await call.message.edit_text(
        f"📊 <b>Store Statistics</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"👥 Total Users: <b>{len(users)}</b>\n"
        f"📦 Total Products: <b>{len(products)}</b>\n"
        f"🕐 Pending Orders: <b>{len(pending)}</b>\n"
        f"━━━━━━━━━━━━━━━━",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Back", callback_data="admin_panel")]
        ]),
        parse_mode="HTML"
    )
    

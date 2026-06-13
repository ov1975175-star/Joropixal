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

BOT_TOKEN = os.getenv("BOT_TOKEN")

def is_admin(user_id):
    return user_id in ADMIN_IDS

class AddProduct(StatesGroup):
    name = State()
    price = State()
    description = State()
    photo_url = State()
    product_file = State()

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
        has_file = "📁" if p.get('product_file_id') else "⚠️"
        buttons.append([
            InlineKeyboardButton(
                text=f"{status}{has_file} {p['name']} — ₹{p['price']}",
                callback_data=f"admin_product_detail:{p['id']}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="➕ Add New Product", callback_data="add_product")])
    buttons.append([InlineKeyboardButton(text="◀️ Back", callback_data="admin_panel")])

    await call.message.edit_text(
        f"📦 <b>Products ({len(products)})</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"✅=Active  ❌=Inactive  📁=File Ready  ⚠️=No File",
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
    file_status = "📁 Ready" if product.get('product_file_id') else "⚠️ No File Uploaded"
    file_type = product.get('product_file_type', 'unknown')

    text = (
        f"📦 <b>{product['name']}</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"💰 Price: ₹{product['price']}\n"
        f"📝 {product.get('description', 'No description')}\n"
        f"🖼️ Thumbnail: {'✅' if product.get('photo_url') else '❌'}\n"
        f"📁 Product File: {file_status}\n"
        f"🗂️ File Type: {file_type}\n"
        f"Status: {status}"
    )

    toggle_text = "❌ Deactivate" if product.get('active', True) else "✅ Activate"
    buttons = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=toggle_text, callback_data=f"toggle_product:{product_id}")],
        [InlineKeyboardButton(text="📁 Update Product File", callback_data=f"update_file:{product_id}")],
        [InlineKeyboardButton(text="🗑️ Delete Product", callback_data=f"del_product_confirm:{product_id}")],
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


# ─── ADD PRODUCT FLOW ───────────────────────────────────────────

@router.callback_query(F.data == "add_product")
async def add_product_start(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        return
    await call.message.answer(
        "📦 <b>Add New Product</b>\n\nStep 1/5 — Enter product <b>name</b>:",
        parse_mode="HTML"
    )
    await state.set_state(AddProduct.name)
    await call.answer()


@router.message(AddProduct.name)
async def add_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("💰 Step 2/5 — Enter <b>price</b> (numbers only, e.g. 99):", parse_mode="HTML")
    await state.set_state(AddProduct.price)


@router.message(AddProduct.price)
async def add_price(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Numbers only! Try again:")
        return
    await state.update_data(price=int(message.text))
    await message.answer("📝 Step 3/5 — Enter product <b>description</b>:", parse_mode="HTML")
    await state.set_state(AddProduct.description)


@router.message(AddProduct.description)
async def add_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer(
        "🖼️ Step 4/5 — Send <b>thumbnail image</b> for this product\n\n"
        "(Display ke liye — product listing mein dikhega)\n"
        "Ya type karo <b>skip</b>:",
        parse_mode="HTML"
    )
    await state.set_state(AddProduct.photo_url)


@router.message(AddProduct.photo_url)
async def add_photo(message: Message, state: FSMContext):
    photo_url = ""
    if message.text and message.text.lower() == "skip":
        photo_url = ""
    elif message.photo:
        photo_url = message.photo[-1].file_id
    elif message.text:
        photo_url = message.text
    await state.update_data(photo_url=photo_url)
    await message.answer(
        "📁 Step 5/5 — Ab <b>actual product file</b> bhejo\n\n"
        "✅ Koi bhi file bhej sakte ho:\n"
        "• PDF, Image, Video\n"
        "• ZIP, APK, Text file\n"
        "• Ya koi bhi document\n\n"
        "⚡ Ye file approve hone ke baad user ko automatically mil jaayegi!",
        parse_mode="HTML"
    )
    await state.set_state(AddProduct.product_file)


@router.message(AddProduct.product_file)
async def add_product_file(message: Message, state: FSMContext):
    file_id = None
    file_type = None

    if message.document:
        file_id = message.document.file_id
        file_type = "document"
    elif message.photo:
        file_id = message.photo[-1].file_id
        file_type = "photo"
    elif message.video:
        file_id = message.video.file_id
        file_type = "video"
    elif message.audio:
        file_id = message.audio.file_id
        file_type = "audio"
    elif message.animation:
        file_id = message.animation.file_id
        file_type = "animation"
    elif message.sticker:
        file_id = message.sticker.file_id
        file_type = "sticker"

    if not file_id:
        await message.answer("❌ Koi file nahi mili! Please ek file bhejo:")
        return

    data = await state.get_data()

    product_id = db.add_product(
        name=data['name'],
        price=data['price'],
        description=data['description'],
        photo_url=data.get('photo_url', ''),
        qr_url='',
        product_file_id=file_id,
        product_file_type=file_type
    )
    await state.clear()

    await message.answer(
        f"✅ <b>Product Added Successfully!</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"📦 Name: <b>{data['name']}</b>\n"
        f"💰 Price: ₹{data['price']}\n"
        f"📝 {data['description']}\n"
        f"🖼️ Thumbnail: {'✅' if data.get('photo_url') else '❌'}\n"
        f"📁 Product File: ✅ ({file_type})\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"📢 Sabko broadcast ho raha hai...",
        parse_mode="HTML"
    )

    # ─── AUTO BROADCAST TO ALL USERS ────────────────────────────
    users = db.get_all_users()
    bot_info = await message.bot.get_me()

    broadcast_text = (
        f"╔══════════════════╗\n"
        f"║  🔥 <b>NEW PRODUCT ALERT!</b> 🔥\n"
        f"╚══════════════════╝\n\n"
        f"🎯 <b>{data['name']}</b>\n\n"
        f"📝 {data['description']}\n\n"
        f"┌─────────────────┐\n"
        f"│  💰 Price: <b>₹{data['price']}</b> ONLY!\n"
        f"└─────────────────┘\n\n"
        f"⚡ <i>Limited Stock — Jaldi Karo!</i>\n"
        f"🛒 Abhi order karo! 👇"
    )

    buy_button = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🛒 Abhi Kharido!",
            url=f"https://t.me/{bot_info.username}"
        )]
    ])

    sent = 0
    failed = 0
    for u in users:
        try:
            uid = int(u['user_id'])
            if data.get('photo_url'):
                await message.bot.send_photo(
                    uid,
                    photo=data['photo_url'],
                    caption=broadcast_text,
                    parse_mode="HTML",
                    reply_markup=buy_button
                )
            else:
                await message.bot.send_message(
                    uid,
                    broadcast_text,
                    parse_mode="HTML",
                    reply_markup=buy_button
                )
            sent += 1
        except:
            failed += 1

    await message.answer(
        f"🎉 <b>Broadcast Complete!</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"✅ Sent: <b>{sent}</b>\n"
        f"❌ Failed: <b>{failed}</b>",
        parse_mode="HTML"
    )


# ─── UPDATE PRODUCT FILE ────────────────────────────────────────

class UpdateFile(StatesGroup):
    waiting_file = State()

@router.callback_query(F.data.startswith("update_file:"))
async def update_file_start(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        return
    product_id = call.data.split(":")[1]
    await state.update_data(update_product_id=product_id)
    await call.message.answer(
        "📁 <b>Update Product File</b>\n\nNaya product file bhejo (PDF/Image/Video/ZIP — kuch bhi):",
        parse_mode="HTML"
    )
    await state.set_state(UpdateFile.waiting_file)
    await call.answer()


@router.message(UpdateFile.waiting_file)
async def update_file_done(message: Message, state: FSMContext):
    file_id = None
    file_type = None

    if message.document:
        file_id = message.document.file_id
        file_type = "document"
    elif message.photo:
        file_id = message.photo[-1].file_id
        file_type = "photo"
    elif message.video:
        file_id = message.video.file_id
        file_type = "video"
    elif message.audio:
        file_id = message.audio.file_id
        file_type = "audio"
    elif message.animation:
        file_id = message.animation.file_id
        file_type = "animation"

    if not file_id:
        await message.answer("❌ File nahi mili! Dobara bhejo:")
        return

    data = await state.get_data()
    product_id = data['update_product_id']
    db.update_product(product_id, {
        "product_file_id": file_id,
        "product_file_type": file_type
    })
    await state.clear()
    await message.answer(
        f"✅ <b>Product file updated!</b>\n"
        f"🗂️ Type: {file_type}\n"
        f"📁 File ID saved successfully.",
        parse_mode="HTML"
    )


# ─── DELETE PRODUCT ─────────────────────────────────────────────

@router.callback_query(F.data.startswith("del_product_confirm:"))
async def delete_product_confirm(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return
    product_id = call.data.split(":")[1]
    product = db.get_product(product_id)
    await call.message.edit_text(
        f"🗑️ <b>Delete Confirmation</b>\n\n"
        f"Kya aap sure hain?\n"
        f"Product: <b>{product['name']}</b> delete ho jaayega!",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Haan, Delete Karo", callback_data=f"del_product:{product_id}"),
                InlineKeyboardButton(text="❌ Cancel", callback_data=f"admin_product_detail:{product_id}")
            ]
        ]),
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


# ─── PENDING ORDERS ─────────────────────────────────────────────

@router.callback_query(F.data == "admin_pending")
async def admin_pending(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return

    orders = db.get_pending_orders()
    if not orders:
        await call.message.edit_text(
            "🕐 <b>Pending Orders</b>\n━━━━━━━━━━━━━━━━\n\n✅ Koi pending order nahi hai!",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="◀️ Back", callback_data="admin_panel")]
            ]),
            parse_mode="HTML"
        )
        return

    await call.message.edit_text(
        f"🕐 <b>Pending Orders ({len(orders)})</b>\n━━━━━━━━━━━━━━━━\n\nSending details...",
        parse_mode="HTML"
    )

    for o in orders:
        product_id = o.get('product_id', '')
        product = db.get_product(product_id) if product_id else None
        file_ready = "📁 File Ready" if (product and product.get('product_file_id')) else "⚠️ No File"

        await call.message.answer(
            f"🕐 <b>Pending Order</b>\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"👤 @{o.get('username','N/A')}\n"
            f"📦 {o['product_name']} — ₹{o['price']}\n"
            f"{file_ready}\n"
            f"🔖 Order ID: <code>{o['id'][:8]}</code>",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="✅ Approve & Send", callback_data=f"approve:{o['id']}:{o['user_id']}"),
                    InlineKeyboardButton(text="❌ Reject", callback_data=f"reject:{o['id']}:{o['user_id']}")
                ]
            ]),
            parse_mode="HTML"
        )
    await call.answer()


# ─── APPROVE ORDER ───────────────────────────────────────────────

@router.callback_query(F.data.startswith("approve:"))
async def approve_order(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return

    parts = call.data.split(":")
    order_id = parts[1]
    user_id = int(parts[2])
    order = db.get_order(order_id)
    db.update_order(order_id, {"status": "approved"})

    product_id = order.get('product_id')
    product = db.get_product(product_id) if product_id else None

    bot = Bot(token=BOT_TOKEN)
    try:
        await bot.send_message(
            user_id,
            f"🎉 <b>Payment Approved!</b>\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"✅ <b>{order['product_name']}</b> confirm ho gaya!\n\n"
            f"📦 Aapka product aa raha hai...",
            parse_mode="HTML"
        )

        if product and product.get('photo_url'):
            try:
                await bot.send_photo(
                    user_id,
                    photo=product['photo_url'],
                    caption=f"🖼️ <b>{product['name']}</b>",
                    parse_mode="HTML"
                )
            except Exception as e:
                print(f"Thumbnail error: {e}")

        if product:
            await bot.send_message(
                user_id,
                f"📦 <b>Product Details</b>\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"🏷️ <b>{product['name']}</b>\n"
                f"💰 ₹{product['price']}\n"
                f"📝 {product.get('description', '')}\n"
                f"━━━━━━━━━━━━━━━━",
                parse_mode="HTML"
            )

        if product and product.get('product_file_id'):
            file_id = product['product_file_id']
            file_type = product.get('product_file_type', 'document')
            caption = f"📁 <b>Aapka Product: {product['name']}</b>\n🙏 Thank you for your purchase!"

            if file_type == "photo":
                await bot.send_photo(user_id, photo=file_id, caption=caption, parse_mode="HTML")
            elif file_type == "video":
                await bot.send_video(user_id, video=file_id, caption=caption, parse_mode="HTML")
            elif file_type == "audio":
                await bot.send_audio(user_id, audio=file_id, caption=caption, parse_mode="HTML")
            elif file_type == "animation":
                await bot.send_animation(user_id, animation=file_id, caption=caption, parse_mode="HTML")
            else:
                await bot.send_document(user_id, document=file_id, caption=caption, parse_mode="HTML")
        else:
            await bot.send_message(
                user_id,
                f"📦 <b>{order['product_name']}</b>\n\n"
                f"✅ Payment approved!\n"
                f"⏳ Product file jald bheja jaayega.",
                parse_mode="HTML"
            )
            await call.message.answer(
                "⚠️ <b>Warning:</b> Is product ki file upload nahi ki thi!",
                parse_mode="HTML"
            )

    except Exception as e:
        print(f"Approve error: {e}")
        await call.message.answer(f"⚠️ Error: {e}", parse_mode="HTML")
    finally:
        await bot.session.close()

    await call.message.edit_text(
        call.message.text + "\n\n✅ <b>APPROVED — PRODUCT FILE SENT TO USER</b>",
        parse_mode="HTML"
    )
    await call.answer("✅ Approved & Product Sent!")


# ─── REJECT ORDER ────────────────────────────────────────────────

@router.callback_query(F.data.startswith("reject:"))
async def reject_order(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return

    parts = call.data.split(":")
    order_id = parts[1]
    user_id = int(parts[2])
    db.update_order(order_id, {"status": "rejected"})

    bot = Bot(token=BOT_TOKEN)
    try:
        await bot.send_message(
            user_id,
            f"❌ <b>Payment Rejected</b>\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"Sorry, payment verify nahi ho saka.\n\n"
            f"Agar galti lage toh support se contact karo.",
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"Reject notify error: {e}")
    finally:
        await bot.session.close()

    await call.message.edit_text(
        call.message.text + "\n\n❌ <b>REJECTED & USER NOTIFIED</b>",
        parse_mode="HTML"
    )
    await call.answer("❌ Rejected!")


# ─── USERS & STATS ──────────────────────────────────────────────

@router.callback_query(F.data == "admin_users")
async def admin_users(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return

    users = db.get_all_users()
    tex

import os
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from FirebaseService import FirebaseService

router = Router()
db = FirebaseService()

ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)


def is_admin(user_id):
    return user_id in ADMIN_IDS


class AddProduct(StatesGroup):
    name = State()
    price = State()
    description = State()
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
        [InlineKeyboardButton(text="🔙 Back", callback_data="go_home")]
    ])


@router.callback_query(F.data == "admin_panel")
async def admin_panel(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("❌ Access Denied!", show_alert=True)
        return

    users = db.get_all_users()
    orders = db.get_pending_orders()

    await call.message.edit_text(
        f"⚙️ <b>Admin Panel</b>\n\n"
        f"👥 Users: {len(users)}\n"
        f"🕐 Pending Orders: {len(orders)}",
        reply_markup=admin_menu(),
        parse_mode="HTML"
    )


# ─── PRODUCTS MANAGEMENT ────────────────────────────────────

@router.callback_query(F.data == "admin_products")
async def admin_products(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return

    products = db.get_all_products()
    buttons = []
    for p in products:
        buttons.append([
            InlineKeyboardButton(text=f"📦 {p['name']} — ₹{p['price']}", callback_data=f"edit_product:{p['id']}"),
            InlineKeyboardButton(text="🗑️", callback_data=f"del_product:{p['id']}")
        ])
    buttons.append([InlineKeyboardButton(text="➕ Add New Product", callback_data="add_product")])
    buttons.append([InlineKeyboardButton(text="🔙 Back", callback_data="admin_panel")])

    await call.message.edit_text(
        "📦 <b>Products:</b>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "add_product")
async def add_product_start(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        return
    await call.message.answer("📦 Enter product <b>name</b>:", parse_mode="HTML")
    await state.set_state(AddProduct.name)
    await call.answer()


@router.message(AddProduct.name)
async def add_product_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("💰 Enter product <b>price</b> (numbers only e.g. 99):", parse_mode="HTML")
    await state.set_state(AddProduct.price)


@router.message(AddProduct.price)
async def add_product_price(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Please enter numbers only!")
        return
    await state.update_data(price=int(message.text))
    await message.answer("📝 Enter product <b>description</b>:", parse_mode="HTML")
    await state.set_state(AddProduct.description)


@router.message(AddProduct.description)
async def add_product_desc(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer(
        "📲 Send your <b>QR code image URL</b>\n\n"
        "(Upload image to imgbb.com and paste the direct link)\n"
        "Or type <b>skip</b> to add later:",
        parse_mode="HTML"
    )
    await state.set_state(AddProduct.qr_url)


@router.message(AddProduct.qr_url)
async def add_product_qr(message: Message, state: FSMContext):
    qr_url = "" if message.text.lower() == "skip" else message.text
    data = await state.get_data()
    product_id = db.add_product(
        name=data['name'],
        price=data['price'],
        description=data['description'],
        qr_url=qr_url
    )
    await state.clear()
    await message.answer(
        f"✅ <b>Product Added!</b>\n\n"
        f"📦 Name: {data['name']}\n"
        f"💰 Price: ₹{data['price']}\n"
        f"🆔 ID: {product_id}",
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("del_product:"))
async def delete_product(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return
    product_id = call.data.split(":")[1]
    db.delete_product(product_id)
    await call.answer("🗑️ Product deleted!", show_alert=True)
    # Refresh products list
    await admin_products(call)


# ─── ORDERS MANAGEMENT ──────────────────────────────────────

@router.callback_query(F.data == "admin_pending")
async def admin_pending(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return

    orders = db.get_pending_orders()
    if not orders:
        await call.answer("No pending orders!", show_alert=True)
        return

    for o in orders:
        await call.message.answer(
            f"🕐 <b>Pending Order</b>\n\n"
            f"👤 User: @{o.get('username', 'N/A')} (ID: {o['user_id']})\n"
            f"📦 Product: {o['product_name']}\n"
            f"💵 Amount: ₹{o['price']}\n"
            f"🆔 Order: {o['id']}",
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

    _, order_id, user_id = call.data.split(":")
    order = db.get_order(order_id)

    db.update_order(order_id, {"status": "approved"})

    # Notify user
    try:
        await bot.send_message(
            int(user_id),
            f"✅ <b>Payment Verified!</b>\n\n"
            f"📦 Your product <b>{order['product_name']}</b> has been approved!\n\n"
            f"🎉 Thank you for your purchase!",
            parse_mode="HTML"
        )
    except Exception:
        pass

    await call.message.edit_text(
        call.message.text + "\n\n✅ <b>APPROVED</b>",
        parse_mode="HTML"
    )
    await call.answer("✅ Order approved and user notified!")


@router.callback_query(F.data.startswith("reject:"))
async def reject_order(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return

    _, order_id, user_id = call.data.split(":")
    db.update_order(order_id, {"status": "rejected"})

    try:
        await bot.send_message(
            int(user_id),
            "❌ <b>Payment Rejected</b>\n\nYour payment could not be verified. "
            "Please contact support if you believe this is an error.",
            parse_mode="HTML"
        )
    except Exception:
        pass

    await call.message.edit_text(
        call.message.text + "\n\n❌ <b>REJECTED</b>",
        parse_mode="HTML"
    )
    await call.answer("❌ Order rejected!")


# ─── USERS & STATS ──────────────────────────────────────────

@router.callback_query(F.data == "admin_users")
async def admin_users(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return
    users = db.get_all_users()
    text = f"👥 <b>Total Users: {len(users)}</b>\n\n"
    for u in users[:20]:
        text += f"• @{u.get('username', 'N/A')} — {u.get('full_name', '')}\n"
    if len(users) > 20:
        text += f"\n...and {len(users)-20} more"

    await call.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Back", callback_data="admin_panel")]
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
        f"📊 <b>Statistics</b>\n\n"
        f"👥 Total Users: {len(users)}\n"
        f"📦 Total Products: {len(products)}\n"
        f"🕐 Pending Orders: {len(pending)}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Back", callback_data="admin_panel")]
        ]),
        parse_mode="HTML"
      )
  

import os
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from FirebaseService import FirebaseService

router = Router()
db = FirebaseService()

ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)

def main_menu(is_admin=False):
    buttons = [
        [InlineKeyboardButton(text="🛍️ Products", callback_data="show_products")],
        [
            InlineKeyboardButton(text="📦 My Purchases", callback_data="my_purchases"),
            InlineKeyboardButton(text="💬 Support", callback_data="support")
        ],
    ]
    if is_admin:
        buttons.append([InlineKeyboardButton(text="⚙️ Admin Panel", callback_data="admin_panel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.message(Command("start"))
async def start_handler(message: Message):
    user = message.from_user
    db.save_user(user.id, user.username or "", user.full_name)
    is_admin = user.id in ADMIN_IDS
    await message.answer(
        f"👋 Welcome, <b>{user.full_name}</b>!\n\n👇 What would you like to do?",
        reply_markup=main_menu(is_admin),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "show_products")
async def show_products(call: CallbackQuery):
    products = db.get_all_products()
    if not products:
        await call.answer("No products available right now.", show_alert=True)
        return

    buttons = []
    for p in products:
        if p.get('active', True):
            buttons.append([
                InlineKeyboardButton(
                    text=f"🛒 {p['name']} — ₹{p['price']}",
                    callback_data=f"buy:{p['id']}"
                )
            ])
    buttons.append([InlineKeyboardButton(text="🔙 Back", callback_data="go_home")])

    await call.message.edit_text(
        "🛍️ <b>Available Products:</b>\n\nClick a product to buy:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("buy:"))
async def buy_product(call: CallbackQuery):
    product_id = call.data.split(":")[1]
    product = db.get_product(product_id)
    if not product:
        await call.answer("Product not found!", show_alert=True)
        return

    text = (
        f"🛒 <b>{product['name']}</b>\n\n"
        f"💰 Price: <b>₹{product['price']}</b>\n\n"
        f"📝 {product.get('description', '')}\n\n"
        f"📲 <b>Scan the QR below to pay:</b>"
    )

    buttons = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ I've Paid — Send Screenshot", callback_data=f"paid:{product_id}")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="show_products")]
    ])

    # Send QR image
    if product.get('qr_url'):
        await call.message.answer_photo(
            photo=product['qr_url'],
            caption=text,
            reply_markup=buttons,
            parse_mode="HTML"
        )
        await call.message.delete()
    else:
        await call.message.edit_text(text, reply_markup=buttons, parse_mode="HTML")


@router.callback_query(F.data.startswith("paid:"))
async def paid_handler(call: CallbackQuery):
    product_id = call.data.split(":")[1]
    product = db.get_product(product_id)
    user = call.from_user

    order_id = db.create_order(
        user_id=user.id,
        username=user.username or user.full_name,
        product_id=product_id,
        product_name=product['name'],
        price=product['price']
    )

    # Notify admins
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(
                admin_id,
                f"💰 <b>New Payment Received!</b>\n\n"
                f"👤 User: @{user.username or user.full_name} (ID: {user.id})\n"
                f"📦 Product: {product['name']}\n"
                f"💵 Amount: ₹{product['price']}\n"
                f"🆔 Order ID: {order_id}\n\n"
                f"⬇️ Verify and approve:",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(text="✅ Approve", callback_data=f"approve:{order_id}:{user.id}"),
                        InlineKeyboardButton(text="❌ Reject", callback_data=f"reject:{order_id}:{user.id}")
                    ]
                ]),
                parse_mode="HTML"
            )
        except Exception:
            pass

    await call.message.answer(
        "📸 Please send your payment screenshot now.\n\n"
        "⏳ Admin will verify and deliver your product shortly!"
    )
    await call.answer()


@router.message(F.photo)
async def receive_screenshot(message: Message):
    user = message.from_user
    # Forward screenshot to all admins
    for admin_id in ADMIN_IDS:
        try:
            await bot.forward_message(admin_id, message.chat.id, message.message_id)
            await bot.send_message(
                admin_id,
                f"📸 Screenshot from @{user.username or user.full_name} (ID: {user.id})"
            )
        except Exception:
            pass
    await message.answer("✅ Screenshot received! Please wait for admin verification.")


@router.callback_query(F.data == "my_purchases")
async def my_purchases(call: CallbackQuery):
    orders = db.get_user_orders(call.from_user.id)
    if not orders:
        await call.answer("You have no approved purchases yet.", show_alert=True)
        return

    text = "📦 <b>Your Purchases:</b>\n\n"
    for o in orders:
        text += f"• {o['product_name']} — ₹{o['price']} ✅\n"

    await call.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Back", callback_data="go_home")]
        ]),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "support")
async def support_handler(call: CallbackQuery):
    await call.message.edit_text(
        "💬 <b>Support</b>\n\nContact admin for help: @YourAdminUsername",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Back", callback_data="go_home")]
        ]),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "go_home")
async def go_home(call: CallbackQuery):
    is_admin = call.from_user.id in ADMIN_IDS
    await call.message.edit_text(
        f"👇 What would you like to do?",
        reply_markup=main_menu(is_admin)
  )
  

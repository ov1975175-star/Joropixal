import os
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
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

class PaymentState(StatesGroup):
    waiting_screenshot = State()

def main_menu(is_admin=False):
    buttons = [
        [InlineKeyboardButton(text="🛍️ Browse Products", callback_data="show_products")],
        [
            InlineKeyboardButton(text="📦 My Orders", callback_data="my_purchases"),
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

    welcome = (
        f"✨ <b>Welcome, {user.full_name}!</b>\n\n"
        f"🎉 You've arrived at <b>PixalJoro Store</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"🛍️ Browse our premium products\n"
        f"💳 Easy QR payment\n"
        f"⚡ Fast delivery after verification\n"
        f"━━━━━━━━━━━━━━━━\n\n"
        f"👇 Choose an option below:"
    )
    await message.answer(welcome, reply_markup=main_menu(is_admin), parse_mode="HTML")


@router.callback_query(F.data == "show_products")
async def show_products(call: CallbackQuery):
    products = db.get_all_products()
    active = [p for p in products if p.get('active', True)]

    if not active:
        await call.answer("No products available right now!", show_alert=True)
        return

    buttons = []
    for p in active:
        price_text = "FREE 🎁" if int(p.get('price', 1)) == 0 else f"₹{p['price']}"
        buttons.append([
            InlineKeyboardButton(
                text=f"🛒 {p['name']}  |  {price_text}",
                callback_data=f"product:{p['id']}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="🏠 Home", callback_data="go_home")])

    await call.message.edit_text(
        "🛍️ <b>Our Products</b>\n"
        "━━━━━━━━━━━━━━━━\n"
        "👆 Click any product to view details & buy\n",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        parse_mode="HTML"
    )


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

    file_id = product.get('product_file')
    if not file_id:
        await call.answer("File not available yet!", show_alert=True)
        return

    db.create_order(
        user_id=call.from_user.id,
        username=call.from_user.username or call.from_user.full_name,
        product_id=product_id,
        product_name=product['name'],
        price=0
    )

    await call.answer("Here's your free product! 🎁")

    caption = (
        f"🎁 <b>Your Free Product!</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"📦 <b>{product['name']}</b>\n\n"
        f"Enjoy! 🙏"
    )
    home_btn = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Home", callback_data="go_home")]
    ])

    try:
        await call.message.answer_document(
            document=file_id,
            caption=caption,
            reply_markup=home_btn,
            parse_mode="HTML"
        )
    except:
        try:
            await call.message.answer_photo(
                photo=file_id,
                caption=caption,
                reply_markup=home_btn,
                parse_mode="HTML"
            )
        except:
            await call.message.answer(
                f"🎁 <b>Your Free Product!</b>\n\n📦 <b>{product['name']}</b>\n\n🔗 {file_id}",
                reply_markup=home_btn,
                parse_mode="HTML"
            )


@router.callback_query(F.data.startswith("buy:"))
async def show_qr(call: CallbackQuery, state: FSMContext):
    product_id = call.data.split(":")[1]
    product = db.get_product(product_id)
    if not product:
        await call.answer("Product not found!", show_alert=True)
        return

    order_id = db.create_order(
        user_id=call.from_user.id,
        username=call.from_user.username or call.from_user.full_name,
        product_id=product_id,
        product_name=product['name'],
        price=product['price']
    )

    await state.update_data(
        order_id=order_id,
        product_name=product['name'],
        price=product['price'],
        product_id=product_id
    )
    await state.set_state(PaymentState.waiting_screenshot)

    text = (
        f"💳 <b>Complete Your Payment</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"📦 Product: <b>{product['name']}</b>\n"
        f"💰 Amount: <b>₹{product['price']}</b>\n"
        f"🔖 Order ID: <code>{order_id[:8]}</code>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"📲 <b>Steps:</b>\n"
        f"1️⃣ Scan the QR code below\n"
        f"2️⃣ Pay ₹{product['price']}\n"
        f"3️⃣ Take screenshot of payment\n"
        f"4️⃣ Send screenshot here ⬇️"
    )

    buttons = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Cancel Order", callback_data=f"cancel_order:{order_id}")]
    ])

    if product.get('qr_url'):
        try:
            await call.message.answer_photo(
                photo=product['qr_url'],
                caption=text,
                reply_markup=buttons,
                parse_mode="HTML"
            )
            await call.message.delete()
            await call.answer()
            return
        except:
            pass

    await call.message.answer(
        text + "\n\n⚠️ <i>QR not available. Contact support.</i>",
        reply_markup=buttons,
        parse_mode="HTML"
    )
    await call.answer()


@router.message(PaymentState.waiting_screenshot, F.photo)
async def receive_screenshot(message: Message, state: FSMContext):
    data = await state.get_data()
    order_id = data.get('order_id', 'N/A')
    product_name = data.get('product_name', 'N/A')
    price = data.get('price', 'N/A')
    user = message.from_user

    await state.clear()

    bot = get_bot()
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(
                admin_id,
                f"🔔 <b>New Payment Received!</b>\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"👤 Customer: @{user.username or 'N/A'}\n"
                f"📛 Name: {user.full_name}\n"
                f"🆔 User ID: <code>{user.id}</code>\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"📦 Product: <b>{product_name}</b>\n"
                f"💵 Amount: <b>₹{price}</b>\n"
                f"🔖 Order: <code>{order_id[:8]}</code>\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"📸 Screenshot below ⬇️",
                parse_mode="HTML"
            )
            await bot.forward_message(admin_id, message.chat.id, message.message_id)
            await bot.send_message(
                admin_id,
                f"✅ Approve or ❌ Reject?",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(text="✅ Approve & Deliver", callback_data=f"approve:{order_id}:{user.id}"),
                        InlineKeyboardButton(text="❌ Reject", callback_data=f"reject:{order_id}:{user.id}")
                    ]
                ])
            )
        except Exception as e:
            pass
    await bot.session.close()

    await message.answer(
        "🎉 <b>Screenshot Received Successfully!</b>\n\n"
        "⏳ Our team is verifying your payment...\n"
        "✅ You'll be notified once approved!\n\n"
        "⚡ Usually takes <b>5-10 minutes</b>\n"
        "Thank you for shopping with us! 🙏",
        parse_mode="HTML"
    )


@router.message(PaymentState.waiting_screenshot)
async def wrong_input_payment(message: Message):
    await message.answer(
        "📸 Please send your <b>payment screenshot</b> as a photo!\n\n"
        "Take a screenshot of your payment and send it here.",
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("cancel_order:"))
async def cancel_order(call: CallbackQuery, state: FSMContext):
    order_id = call.data.split(":")[1]
    db.update_order(order_id, {"status": "cancelled"})
    await state.clear()
    is_admin = call.from_user.id in ADMIN_IDS
    await call.message.answer(
        "❌ <b>Order Cancelled</b>\n\nFeel free to browse again!",
        reply_markup=main_menu(is_admin),
        parse_mode="HTML"
    )
    await call.answer("Order cancelled!")


@router.callback_query(F.data == "my_purchases")
async def my_purchases(call: CallbackQuery):
    orders = db.get_user_orders(call.from_user.id)
    if not orders:
        await call.answer("No approved purchases yet!", show_alert=True)
        return

    text = "📦 <b>Your Orders</b>\n━━━━━━━━━━━━━━━━\n\n"
    for o in orders:
        text += f"✅ <b>{o['product_name']}</b> — ₹{o['price']}\n"

    await call.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Home", callback_data="go_home")]
        ]),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "support")
async def support_handler(call: CallbackQuery):
    await call.message.edit_text(
        "💬 <b>Customer Support</b>\n"
        "━━━━━━━━━━━━━━━━\n\n"
        "📞 For any issues, contact our admin directly.\n\n"
        "⏰ Response time: <b>Within 1 hour</b>\n"
        "━━━━━━━━━━━━━━━━",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Home", callback_data="go_home")]
        ]),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "go_home")
async def go_home(call: CallbackQuery):
    is_admin = call.from_user.id in ADMIN_IDS
    try:
        await call.message.edit_text(
            "👇 What would you like to do?",
            reply_markup=main_menu(is_admin)
        )
    except:
        await call.message.answer(
            "👇 What would you like to do?",
            reply_markup=main_menu(is_admin)
    )

from aiogram import Router, F, Bot # Bot aur Router add kiya
from aiogram.types import CallbackQuery
from FirebaseService import FirebaseService # Firebase import kiya

# YE LINE ZARURI HAI
router = Router() 
firebase = FirebaseService()
ADMIN_ID = "YOUR_ADMIN_ID_HERE" # Apna Admin ID yahan likhein
bot = Bot(token="YOUR_BOT_TOKEN_HERE") 

@router.callback_query(F.data.startswith("verify_payment:"))
async def handle_verify_payment(call: CallbackQuery):
    # ... aapka baki ka code bilkul sahi hai ...
    order_id = call.data.split(":")[1]
    # ...
    

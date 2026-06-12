import asyncio
from aiogram import Bot, Dispatcher
from bot.handlers import user, admin

async def main():
    # Apna Token yahan daalein
    bot = Bot(token="8001535871:AAEr-DvtKgP3XggXNqih-rzy1Yfjx4UqAhI")
    dp = Dispatcher()

    # Routers register karein
    dp.include_router(user.router)
    dp.include_router(admin.router)

    print("Bot is running...")
    # Polling mode: Webhook error se bachne ke liye
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    

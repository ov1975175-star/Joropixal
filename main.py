import asyncio
from aiogram import Bot, Dispatcher
from bot.handlers.user import router as user_router
from bot.handlers.admin import router as admin_router

async def main():
    bot = Bot(token="8001535871:AAEr-DvtKgP3XggXNqih-rzy1Yfjx4UqAhI")
    dp = Dispatcher()

    dp.include_router(user_router)
    dp.include_router(admin_router)

    print("Bot is running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
  

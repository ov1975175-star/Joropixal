# main.py mein
from bot.handlers import user_router, admin_router

# Dono ka naam alag hai toh include_router sahi se chalega
dp.include_router(user_router)
dp.include_router(admin_router)

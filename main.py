import sys
import os

# Root directory ko path mein add karein
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

import asyncio
from aiogram import Bot, Dispatcher
from fastapi import FastAPI
import uvicorn
import threading
from bot.handlers import user, admin

# ... baaki code same rahega ...

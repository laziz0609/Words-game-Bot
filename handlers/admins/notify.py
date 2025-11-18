from aiogram import Router, types
from aiogram.filters import Command
import os

router = Router()
ADMINS = os.getenv("ADMINS", "").split(",")

@router.message(Command("admin"))
async def admin_panel(message: types.Message):
    if str(message.from_user.id) not in ADMINS:
        return await message.answer("⛔ Siz admin emassiz!")
    await message.answer("👑 Admin panelga xush kelibsiz!")

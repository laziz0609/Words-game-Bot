from aiogram import Router, types
from aiogram.filters import Command

router = Router()

@router.message(Command("stats"))
async def show_stats(message: types.Message):
    await message.answer("📊 Bot statistikasi: aktiv, foydalanuvchilar soni noma’lum.")

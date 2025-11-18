import logging

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


from keyboards.default.reply_menu import menu_kb
from states.check_user_state import Check_user
from data.db_users_functions import get_user , save_user

router = Router()

@router.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    name = await get_user(message.from_user.id)
    if name:
        current_state = await state.get_state()
        if current_state is not None:
            await state.clear()
        await message.answer(
            f"Assalomu alaykum, <b>{name}</b>! 😊\nSizni yana ko‘rganimdan xursandman!",
            parse_mode="HTML",
            reply_markup=menu_kb
        )
    else:
        keyboard = ReplyKeyboardMarkup(
             keyboard=[
                [KeyboardButton(text=f"{message.from_user.first_name}")]
            ],
            resize_keyboard=True
        )
        await message.answer(
            "😊 Ismingizni kiriting, yoki pastdagi tugmani bosing 👇",
            reply_markup=keyboard
        )
        await state.set_state(Check_user.check)
        
        
@router.message(Check_user.check)
async def name_input(message: types.Message, state: FSMContext):
    if message.text:
        text = message.text.strip()
        if text[0].isalpha():
            if message.text == '/start':
                await message.answer("Iltimos ismingizni kiriting")
            else:
                name = message.text.capitalize()
                await save_user(message.from_user.id, name)
                await message.answer(
                    f"✅ Ismingiz <b>{name}</b> sifatida saqlandi!",
                    parse_mode="HTML",
                    reply_markup=menu_kb
                )
                await state.clear()
        else:
            await message.answer("❗ Iltimos, ism faqat harflardan tashkil topishi kerak. Qayta kiriting.")
    

    

from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext


from keyboards.default.reply_menu import menu_kb
from states.change_name_state import Change_name
from data.db_users_functions import save_user , get_user

router = Router()



@router.message(F.text == "✍️ Ismni yangilash")
async def change_name_handler(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="❌ Bekor qilish")]],
        resize_keyboard=True)
    
    name = await get_user(message.from_user.id)
    await message.answer(f"Hozirgi nomingiz <b>{name}</b>\nIltimos, yangi nomingizni kiriting:", reply_markup=keyboard, parse_mode="HTML")
    await state.set_state(Change_name.waiting_for_new_name)

@router.message(Change_name.waiting_for_new_name, F.text)
async def process_new_name(message: types.Message, state: FSMContext):
    new_name = message.text.strip()
    
    if new_name.lower() == "❌ bekor qilish" or new_name.lower() == "/start":
        await message.answer("Ism o'zgartirish bekor qilindi.", reply_markup=menu_kb)
        await state.clear()
        return
    
    if new_name[0].isalpha():
        await save_user(message.from_user.id, new_name)
        await message.answer(f"Sizning ismingiz muvaffaqiyatli yangilandi: {new_name}", reply_markup=menu_kb)
        await state.clear()
    else:
        await message.answer("❗ Iltimos, ism faqat harflardan tashkil topishi kerak. Qayta kiriting.")



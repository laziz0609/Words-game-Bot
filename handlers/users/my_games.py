import aiofiles
import json
import os
import re

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton



from keyboards.inline.my_games_inline import my_games_button, game_config, delete_game_kb, MyGamesCallbackData
from data.db_games_functions import get_dates_all , get_file_path, delete_game_data, update_words_number
from states.my_games_state import My_Games
from keyboards.default.reply_menu import menu_kb

router = Router()



#foydalanvchini o'yinchilarini ko'rish
@router.message(F.text == "📂 Mening o‘yinlarim")
async def my_games_hand(message: types.Message):
    keyboard = await my_games_button(message.from_user.id)
    if not keyboard:
        await message.answer("Sizda hozircha o'yinlar mavjud emas.")
        return
    await message.answer("Sizninig o'yinlaringiz", reply_markup=keyboard)



# foydalanuvhininig o'yini malumotlarini ko'rish
@router.callback_query(MyGamesCallbackData.filter())
async def my_game_info(callback_query: types.CallbackQuery, callback_data: MyGamesCallbackData, state: FSMContext):
    game_id = callback_data.game_id
    
    info = await get_dates_all(game_id)
    user_id , game_name , creator_name , words_number = info
    url = f"tg://user?id={user_id}"
    text = f"""
    👤 <b>Yaratuvchi:</b> <a href="{url}">{creator_name}</a>
    📚 <b>So'zlar soni:</b> {words_number} ta
    📝 <b>O'yin nomi:</b> {game_name}
    🆔 <b>ID:</b> <code>{game_id}</code>
    """
    
    try:
        await callback_query.message.delete()
    except Exception as e:
        print(f"ERROR , Xabarni o'chirib bo'lmadi: {e}")
    await callback_query.message.answer("<b>🎮 O'yin ma'lumotlari</b>", reply_markup=types.ReplyKeyboardRemove(), parse_mode="HTML")
    await callback_query.message.answer(text, reply_markup=game_config, parse_mode="HTML")
    await callback_query.answer()
    
    await state.set_state(My_Games.viewing_game)
    await state.update_data(game_id=game_id)
    



# orqaga qaytish
@router.callback_query(F.data == "back_to_menu", My_Games.viewing_game)
async def back_to_my_games(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        await callback_query.message.delete()
    except Exception as e:
        print(f"ERROR , Xabarni o'chirib bo'lmadi: {e}")
    await callback_query.message.answer("Sizninig o'yinlaringiz", reply_markup=menu_kb)
    await callback_query.message.answer("\u2063", reply_markup=await my_games_button(callback_query.from_user.id))
    await callback_query.answer()
    await state.clear()
    
      
# bosh menu ga qaytish
@router.callback_query(F.data == "to_main_menu", My_Games.viewing_game)
async def back_to_main_menu(callback_query: types.CallbackQuery, state: FSMContext):  
    try:
        await callback_query.message.delete()
    except Exception as e:
        print(f"ERROR , Xabarni o'chirib bo'lmadi: {e}")
    await callback_query.message.answer("Asosiy menyu", reply_markup=menu_kb)
    await callback_query.answer()
    await state.clear()  
    



# so'zlarni ko'rish tugmasi
@router.callback_query(F.data == "view_words", My_Games.viewing_game)
async def view_words(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data() # statedan foydalanuvhi kiritgan id raqamini olamiz
    game_id = data.get("game_id") 
    
    file_path = await get_file_path(game_id)# malumotlar bazasidan id raqamga tegizshi file manzilini aniqlaymiz
   
    # json faylni ochamiz
    async with aiofiles.open(file_path, mode="r", encoding="utf-8") as f:  
        json_words = await f.read()
        words = json.loads(json_words)
    if not words:
        await callback_query.message.answer("🕸 Bu o‘yinda hech qanday so‘z mavjud emas.")
        await callback_query.answer()
        return
    await callback_query.message.delete()
    text = "<b>So'zlar ro'yxati:</b>\n\n"   
    for key , value in words.items():
        for word in value:
            text += f"{key} - {word}\n"
    
    info = await get_dates_all(game_id)
    user_id , game_name , creator_name , words_number = info
    url = f"tg://user?id={user_id}"
    infos = f"""
    <b>🎮 O'yin ma'lumotlari</b>
    👤 <b>Yaratuvchi:</b> <a href="{url}">{creator_name}</a>
    📚 <b>So'zlar soni:</b> {words_number} ta
    📝 <b>O'yin nomi:</b> {game_name}
    🆔 <b>ID:</b> <code>{game_id}</code>
    """
    await callback_query.message.answer(text, parse_mode="HTML")
    await callback_query.message.answer(infos, reply_markup=game_config, parse_mode="HTML")
    await callback_query.answer()
    
    
    
# o'yinni o'chirish tugmasi
@router.callback_query(F.data == "delete_game", My_Games.viewing_game)
async def delete_game(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer("⚠️ Diqqat! Ushbu o‘yinni o‘chirishni tasdiqlaysizmi?", reply_markup=delete_game_kb)
   
    try:
        await callback_query.message.delete()
    except Exception as e:
        print(f"ERROR , Xabarni o'chirib bo'lmadi: {e}")
        
    await callback_query.answer()
    await state.set_state(My_Games.delate_game)

# o'yinni o'chirishni tasdiqlash
@router.callback_query(F.data == "confirm_delete_game", My_Games.delate_game)
async def confirm_delete_game(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data() # statedan foydalanuvhi kiritgan id raqamini olamiz
    game_id = data.get("game_id") 
    
    # json faylni o'chiramiz
    file_path = await get_file_path(game_id)
    try:
        os.remove(file_path)
    except Exception as e:
        print(f"ERROR , Faylni o'chirib bo'lmadi: {e}")
    
    # malumotlar bazasidan o'yinni o'chiramiz
    await delete_game_data(game_id)
    
    
    try:
        await callback_query.message.delete()
    except Exception as e:
        print(f"ERROR , Xabarni o'chirib bo'lmadi: {e}")
        
    await callback_query.message.answer("✅ O‘yiningiz muvaffaqiyatli o‘chirildi.", reply_markup=menu_kb)
    await callback_query.answer()
    await state.clear()

# o'yinni o'chirishni bekor qilish
@router.callback_query(F.data == "cancel_delete_game", My_Games.delate_game)
async def cancel_delete_game(callback_query: types.CallbackQuery, state: FSMContext):   
    data = await state.get_data() # statedan foydalanuvhi kiritgan id raqamini olamiz
    game_id = data.get("game_id")
    
    info = await get_dates_all(game_id)
    user_id , game_name , creator_name , words_number = info
    url = f"tg://user?id={user_id}"
    text = f"""
    👤 <b>Yaratuvchi:</b> <a href="{url}">{creator_name}</a>
    📚 <b>So'zlar soni:</b> {words_number} ta
    📝 <b>O'yin nomi:</b> {game_name}
    🆔 <b>ID:</b> <code>{game_id}</code>
    """
    
    try:
        await callback_query.message.delete()
    except Exception as e:
        print(f"ERROR , Xabarni o'chirib bo'lmadi: {e}")
    await callback_query.message.answer("<b>🎮 O'yin ma'lumotlari</b>", reply_markup=types.ReplyKeyboardRemove(), parse_mode="HTML")
    await callback_query.message.answer(text, reply_markup=game_config, parse_mode="HTML")
    await callback_query.answer()
    
    await state.set_state(My_Games.viewing_game)
    



# so'z qo'shish tugmasi
@router.callback_query(F.data == "add_words", My_Games.viewing_game)
async def add_words(callback_query: types.CallbackQuery, state: FSMContext):
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="💾 Saqlash va yakunlash")],
            ],
        resize_keyboard=True
        ) 
        
        await callback_query.message.delete()  
        await callback_query.message.answer(
            "So'zlarni kiriting\n"
            "Tugatgach, <b>💾 Saqlash va yakunlash</b> tugmasini bosing.",
            parse_mode="HTML",
            reply_markup=keyboard
        )
        await callback_query.answer()
        await state.set_state(My_Games.adding_words)

# so'z qo'shish holati
@router.message(My_Games.adding_words, F.text)
async def adding_words(message: types.Message, state: FSMContext):
    
    # bu funksiya foydalanuvchi yozgan matn biz bergan shablonga to'g'ri kelishi yoki yo'qligini tekshiradi
    def check_word_regex(words: str):
        # " - " ko‘rinishidagi bo‘laklarni sanaymiz
        matches = re.findall(r'\s-\s', words)

        # Agar bitta emas, ko‘p bo‘lsa -> None qaytaramiz
        if len(matches) != 1:
            return None

        # Faqat bitta bo‘lsa, ikkiga bo‘lamiz
        match = re.match(r'^(.*?)\s-\s(.*)$', words.strip())
        if match:
            return match.groups()
        return None
    
    
    
    # so'zlarni saqlash
    if message.text == "💾 Saqlash va yakunlash" or message.text == "/start":
        data = await state.get_data()
        game_id = data.get("game_id")
        adding_words_number = data.get("words_number", 0)
        # statedan foydalanuvchi kiritgan so'zlarni olamiz
        words_dict = data.get("words_dict", {})
        
        # malumotlar bazasidan o'yin fayl manzilini olamiz
        file_path = await get_file_path(game_id)
        
        # json faylni ochamiz
        async with aiofiles.open(file_path, mode="r", encoding="utf-8") as f:  
            json_words = await f.read()
            words = json.loads(json_words)
        
        # yangi so'zlarni json faylga yozamiz
        for key, value in words_dict.items():
            if key in words.keys():
                words[key].extend(value)
            else:
                words[key] = value
                
        # yangilangan lug'atni json faylga yozamiz
        async with aiofiles.open(file_path, mode="w", encoding="utf-8") as f:
            await f.write(json.dumps(words, ensure_ascii=False))
        # so'zlar sonini yangilaymiz
        await update_words_number(game_id, adding_words_number)
        
        info = await get_dates_all(game_id)
        user_id , game_name , creator_name , words_number = info
        url = f"tg://user?id={user_id}"
        text = f"""
        👤 <b>Yaratuvchi:</b> <a href="{url}">{creator_name}</a>
        📚 <b>So'zlar soni:</b> {words_number} ta
        📝 <b>O'yin nomi:</b> {game_name}
        🆔 <b>ID:</b> <code>{game_id}</code>
        """ 
        await message.answer("<b>🎮 O'yin ma'lumotlari</b>", reply_markup=types.ReplyKeyboardRemove(), parse_mode="HTML")
        await message.answer(text, reply_markup=game_config, parse_mode="HTML")
        await state.clear()
        await state.set_state(My_Games.viewing_game)
        await state.update_data(game_id=game_id)
        return 
    
    
    # kiritilgan so'z biz bergan shablonga to'g'ri keladi yoki yo'q shuni tekshirayabmiz
    words = check_word_regex(message.text)
    if not words:
        await message.answer(
            "📘 <b>So‘zlarni kiritish qoidasi:</b>\n\n"
            "So‘z yoki so‘z birikmalarini <b>chiziqcha (-)</b> bilan ajratib yozing.\n"
            "Chiziqchadan oldin va keyin <b>bitta bo‘sh joy</b> bo‘lishi kerak.\n\n"
            "🔹 <b>Misollar:</b>\n"
            "• hello - salom\n"
            "• eat out - restoranda ovqatlanish\n"
            "• check-in - ro‘yxatdan o‘tish\n\n"
            "Har bir juftlikni alohida qatorda yozing.",
            parse_mode="HTML"
        )
    else:
        key, value = words
        key = str(key)
        value = str(value)
        key = key.lower()
        value = value.lower()

        #statega foydalanuvchi yozgan so'zlarni saqlayabmiz
        data = await state.get_data()
        words_dict = data.get("words_dict", {}) # words_dict lug'atini ol agar yo'q bo'lsa yarat
        words_number = data.get("words_number", 0) # foydalanuvchi yozgan lug'atlar soni 0 dan boshlanadi
        
        # foydalanuvhi yozgan so'zlarni kalit , qiymat juftligada words_dict lug'atiga yozamiz
        if key in words_dict.keys():
            words_dict[key].append(value)
        else:
            words_dict[key] = [value]
            
        words_number += 1
        
        await state.update_data(words_dict=words_dict, words_number=words_number)

        await message.answer(f"✅ So‘z qo‘shildi")
    
    
    
    
# so'zlarni o'chirish tugmasi
@router.callback_query(F.data == "delete_words", My_Games.viewing_game)
async def delete_words(callback_query: types.CallbackQuery, state: FSMContext):
    # json faylni ochamiz
    data = await state.get_data() # statedan foydalanuvhi kiritgan id raqamini olamiz
    game_id = data.get("game_id")
    file_path = await get_file_path(game_id)
    async with aiofiles.open(file_path, mode="r", encoding="utf-8") as f:  
        json_words = await f.read()
        words = json.loads(json_words)
    if not words:
        await callback_query.message.answer("🕸 Bu o‘yinda hech qanday so‘z mavjud emas.")
        return
    
    await callback_query.message.answer(
        "O'chirmoqchi bo'lgan so'zni kiriting (kalit so'zni):",
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton(text="⬅️ Orqaga")],
                [types.KeyboardButton(text="📚 So'zlar ro'yxati")]
            ],
            resize_keyboard=True
        )
    )
    try:
        await callback_query.message.delete()
    except Exception as e:
        print(f"ERROR , Xabarni o'chirib bo'lmadi: {e}")
    await callback_query.answer()
    await state.set_state(My_Games.deleting_words)
    await state.update_data(words_dict=words)  # hozirgi so'zlar lug'atini stateda saqlaymiz
    
# so'zlarni o'chirish holati
@router.message(My_Games.deleting_words, F.text)
async def deleting_words(message: types.Message, state: FSMContext):
    data = await state.get_data() # statedan foydalanuvhi kiritgan id raqamini olamiz

    if message.text == "⬅️ Orqaga":
        game_id = data.get("game_id")
        words_dict = data.get("words_dict")
        del_words_number = data.get("del_words_number", 0)
        file_path = await get_file_path(game_id)
        # json faylni ochamiz
        async with aiofiles.open(file_path, mode="w", encoding="utf-8")as f:
            await f.write(json.dumps(words_dict, ensure_ascii=False))
        # so'zlar sonini yangilaymiz
        await update_words_number(game_id, del_words_number) 
        info = await get_dates_all(game_id)
        user_id , game_name , creator_name , words_number = info
        url = f"tg://user?id={user_id}"
        text = f"""
        👤 <b>Yaratuvchi:</b> <a href="{url}">{creator_name}</a>
        📚 <b>So'zlar soni:</b> {words_number} ta
        📝 <b>O'yin nomi:</b> {game_name}
        🆔 <b>ID:</b> <code>{game_id}</code>
        """ 
        await message.answer("<b>🎮 O'yin ma'lumotlari</b>", reply_markup=types.ReplyKeyboardRemove(), parse_mode="HTML")
        await message.answer(text, reply_markup=game_config, parse_mode="HTML")
        await state.clear()
        await state.set_state(My_Games.viewing_game)
        await state.update_data(game_id=game_id)
        return
    
    if message.text == "📚 So'zlar ro'yxati":
        data = await state.get_data()
        words = data.get("words_dict")
        if not words:
            await message.answer("🕸 Bu o‘yinda hech qanday so‘z mavjud emas.")
            return
        text = "<b>So'zlar ro'yxati:</b>\n\n"   
        for key , value in words.items():
            for word in value:
                text += f"{key} - {word}\n"
        await message.answer(text, parse_mode="HTML")
        return
        
    
    delate_word = message.text.lower().strip()
    words_dict = data.get("words_dict")
    del_words_number = data.get("del_words_number", 0)
    
    if delate_word not in words_dict.keys():
        await message.answer("❌ Bunday so‘z (kalit) topilmadi.")
        return
    
    # so'zni lug'atdan o'chiramiz
    num = len(words_dict[delate_word])
    del_words_number -= num
    del words_dict[delate_word]
    await state.update_data(words_dict=words_dict, del_words_number=del_words_number)
    await message.answer(f"✅ So‘z o‘chirildi. {delate_word}")
    
    
        
    
    

        
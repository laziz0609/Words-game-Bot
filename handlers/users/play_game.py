import aiofiles
import json
import random

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext


from keyboards.default.play_game_keyboard import game_or_words, exit_or_words, end_game
from keyboards.default.other_keyboards import back
from keyboards.default.reply_menu import menu_kb
from states.play_game_state import Play_Game
from data.db_games_functions import get_dates_all, get_file_path


router = Router()


@router.message(F.text == "🎮 O‘yin o'ynash")
async def play_games(message: types.Message , state: FSMContext):
    await message.answer(
        "🔢 <b>O‘yin ID raqamini kiriting.</b>\n\n"
        "Masalan: <code>7</code>",
        reply_markup=back,
        parse_mode="HTML"
    )
    await state.set_state(Play_Game.id_input)
    
    
    
    
# foydalanuvchidan kiritgan id olib kerakli o'yinnni topib berish
@router.message(Play_Game.id_input, F.text)
async def put_id(message: types.Message , state: FSMContext):
    if message.text in ["/start", "🔙 Orqaga"]:
        await message.answer("Bosh sahifa" , reply_markup = menu_kb)
        await state.clear()
        return
        
    # foydalanuvchi to'gri turdagi ma'lumot kirityabdimi yoki yo'q tekshirish
    game_id = message.text
    try:
        game_id= int(game_id)
    except:
        await message.answer(
        "⚠️ <b>ID butun son bo‘lishi kerak.</b>\n"
        "Qaytadan kiriting. Masalan: <code>7</code>",
        reply_markup=back,
        parse_mode="HTML"
        )

        return
    
    # foydalanuvchi kiritgan id bo'yicha malumot bormi yoki yo'q tekshirish
    info = await get_dates_all(game_id)
    if not info:
        await message.answer(
            "❌ <b>Bunday ID raqamiga ega o‘yin topilmadi.</b>\n"
            "ID raqamini tekshirib, qaytadan urinib ko‘ring.",
            reply_markup=back,
            parse_mode="HTML"
        )
        return
    
    user_id , game_name , creator_name , words_number = info
    url = f"tg://user?id={user_id}"
    text = f"""
    <b>🎮 O'yin ma'lumotlari</b>\n
    👤 <b>Yaratuvchi:</b> <a href="{url}">{creator_name}</a>
    📚 <b>So'zlar soni:</b> {words_number} ta
    📝 <b>O'yin nomi:</b> {game_name}
    🆔 <b>ID:</b> <code>{game_id}</code>
    """
    await message.answer(text, reply_markup = game_or_words , parse_mode="HTML")
    await state.update_data(game_id = game_id)
    await state.set_state(Play_Game.words_or_game)
    



# bosh sahifaga qaytish
@router.message(Play_Game.words_or_game, F.text == "🏠 Bosh sahifa" or F.text == "/start")
async def home(message: types.Message, state: FSMContext):
    await message.answer("Bosh sahifa" , reply_markup = menu_kb)
    await state.clear()
    
    
    
# so'zlar ro'yxatini ko'rsatish
@router.message(Play_Game.words_or_game, F.text == "📚 So'zlar ro'yxati")
async def print_words_f(message: types.Message, state: FSMContext):
    
    data = await state.get_data() # statedan foydalanuvhi kiritgan id raqamini olamiz
    game_id = data.get("game_id") 
    
    file_path = await get_file_path(game_id)# malumotlar bazasidan id raqamga tegizshi file manzilini aniqlaymiz
   
    # json faylni ochamiz
    async with aiofiles.open(file_path, mode="r", encoding="utf-8") as f:  
        json_words = await f.read()
        words = json.loads(json_words)
    if not words:
        await message.answer("🕸 Bu o‘yinda hech qanday so‘z mavjud emas.")
        return
    text = ""   
    for key , value in words.items():
        for word in value:
            text += f"{key} - {word}\n"
    await message.answer(text)
    

# words game o'yinini boshlash
@router.message(Play_Game.words_or_game, F.text == "🎮 O'yinni boshlash")
async def play_game_f(message: types.Message, state: FSMContext):
    
    data = await state.get_data() # statedan foydalanuvhi kiritgan id raqamini olamiz
    game_id = data.get("game_id") 
    
    file_path = await get_file_path(game_id)# malumotlar bazasidan id raqamga tegizshi file manzilini aniqlaymiz
    
    # json faylni ochamiz
    async with aiofiles.open(file_path, mode="r", encoding="utf-8") as f:  
        json_words = await f.read()
        words = json.loads(json_words)
    if not words:
        await message.answer("🕸 Bu o‘yinda hech qanday so‘z mavjud emas.")
        return
    
    keys = list(words.keys())
    random.shuffle(keys) # so'zlarni random qilib olamiz
    
    # keyingi so'zni tayyorlash
    word = keys.pop(0)
    asked_word = words[word]   
    text = ""
    if len(asked_word) > 1:
        for w in asked_word:
            text += f"{w}, "
    else:
        text = asked_word[0]
        
    await message.answer(
        "✅ <b>O‘yin boshlandi!</b>\n"
        "Sizga so‘zlar ketma-ket yuboriladi.\n"
        "Har bir so‘zning tarjimasini yozing.",
        parse_mode="HTML"
    )
    await message.answer(text, reply_markup=exit_or_words)
    

    correct_answers = 0
    incorrect_answers = []
    total_questions = len(words)
    await state.update_data(asked_word = asked_word, words = words, correct_answers = correct_answers, incorrect_answers = incorrect_answers, total_questions = total_questions, keys=keys, word=word)
    await state.set_state(Play_Game.game)
 
 
 
# o'yinni to'xtatish
@router.message(Play_Game.game, F.text.in_(["⛔ O'yinni to'xtatish", "/start", "🏠 Asosiy menyu"]))
async def stop_game(message: types.Message, state: FSMContext):
    await message.answer(
    "⛔ O‘yin to‘xtatildi.\nSiz bosh menyuga qaytdingiz.",  reply_markup=menu_kb )
    await state.clear()
    
 
 
# orqaga qaytish
@router.message(Play_Game.game, F.text == "🔙 Orqaga")
async def back_game(message: types.Message, state: FSMContext):
    data = await state.get_data() # statedan foydalanuvhi kiritgan id raqamini olamiz
    game_id = data.get("game_id")
    
    info = await get_dates_all(game_id)
    
    user_id , game_name , creator_name , words_number = info
    url = f"tg://user?id={user_id}"
    text = f"""
    <b>🎮 O'yin ma'lumotlari</b>\n
    👤 <b>Yaratuvchi:</b> <a href="{url}">{creator_name}</a>
    📚 <b>So'zlar soni:</b> {words_number} ta
    📝 <b>O'yin nomi:</b> {game_name}
    🆔 <b>ID:</b> <code>{game_id}</code>
    """
    await message.answer(text, reply_markup = game_or_words , parse_mode="HTML")
    await state.set_state(Play_Game.words_or_game)

 


# qayta o'ynash
@router.message(Play_Game.game, F.text == "🎮 Yana o‘ynash")
async def play_game_again(message: types.Message, state: FSMContext):
    
    data = await state.get_data() # statedan foydalanuvhi kiritgan id raqamini olamiz
    game_id = data.get("game_id") 
    
    file_path = await get_file_path(game_id)# malumotlar bazasidan id raqamga tegizshi file manzilini aniqlaymiz
    
    # json faylni ochamiz
    async with aiofiles.open(file_path, mode="r", encoding="utf-8") as f:  
        json_words = await f.read()
        words = json.loads(json_words)
    if not words:
        await message.answer("🕸 Bu o‘yinda hech qanday so‘z mavjud emas.")
        return
    
    keys = list(words.keys())
    random.shuffle(keys) # so'zlarni random qilib olamiz
    
    # keyingi so'zni tayyorlash
    word = keys.pop(0)
    asked_word = words[word]   
    text = ""
    if len(asked_word) > 1:
        for w in asked_word:
            text += f"{w}, "
    else:
        text = asked_word[0]
        
    await message.answer(
        "✅ <b>O‘yin boshlandi!</b>\n"
        "Sizga so‘zlar ketma-ket yuboriladi.\n"
        "Har bir so‘zning tarjimasini yozing.",
        parse_mode="HTML"
    )
    await message.answer(text, reply_markup=exit_or_words)
    

    correct_answers = 0
    incorrect_answers = []
    total_questions = len(words)
    await state.update_data(asked_word = asked_word, words = words, correct_answers = correct_answers, incorrect_answers = incorrect_answers, total_questions = total_questions, keys=keys, word=word)


# topilmagan so'zlar ro'yxati
@router.message(Play_Game.game, F.text == "📋 Topilmagan so‘zlar ro‘yxati")
async def not_found_words(message: types.Message, state: FSMContext):
    data = await state.get_data()
    words = data.get("words")
    incorrect_answers = data.get("incorrect_answers")
    if not incorrect_answers:
        await message.answer("🎉 <b>Ajoyib!</b>\nSiz barcha so‘zlarga to‘g‘ri javob berdingiz!", parse_mode="HTML")
        return
    text = "Topilmagan so'zlar ro'yxati:\n"
    for key in incorrect_answers:
        if len(words[key]) > 1:
            for w in words[key]:
                text += f"{key} - {w}\n"
        else:
            text += f"{key} - {words[key][0]}\n"
    await message.answer(text)
   
    

# o'yin jarayoni
@router.message(Play_Game.game, F.text)
async def game_process(message: types.Message, state: FSMContext):
    data = await state.get_data()
    asked_word = data.get("asked_word")
    words = data.get("words")
    correct_answers = data.get("correct_answers")
    total_questions = data.get("total_questions")
    keys = data.get("keys")
    incorrect_answers = data.get("incorrect_answers")
    word = data.get("word")
    
    answer = message.text.lower()
    # o'yin tugaganmi yoki yo'q tekshirish
    if not keys:
        if answer.strip() == word:
            correct_answers += 1
            await message.answer("✅ To'g'ri javob!")
        else:
            await message.answer(f"❌ Noto‘g‘ri.\nTo‘g‘ri javob: <b>{word}</b>", parse_mode="HTML")
            incorrect_answers.append(word)        
        await message.answer(
            f"🏁 <b>O‘yin tugadi!</b>\n"
            f"✅ To‘g‘ri javoblar:   <b>{correct_answers}</b>\n"
            f"❓ Jami savollar:   <b>{total_questions}</b>",
            reply_markup=end_game,
            parse_mode="HTML"
        )
        return
    
    # foydalanuvchi javobini tekshirish
    if answer.strip() == word:
        correct_answers += 1
        await message.answer("✅ To'g'ri javob!")
    else:
        await message.answer(f"❌ Noto‘g‘ri.\nTo‘g‘ri javob: <b>{word}</b>", parse_mode="HTML")
        incorrect_answers.append(word)
        
    # keyingi so'zni tayyorlash
    word = keys.pop(0)
    asked_word = words[word]   
    text = ""
    if len(asked_word) > 1:
        for w in asked_word:
            text += f"{w}, "
    else:
        text = asked_word[0]
    
    await message.answer(text)
    await state.update_data(asked_word = asked_word, correct_answers = correct_answers, keys=keys, word=word, incorrect_answers=incorrect_answers)
    
    
    
        
    
    

    
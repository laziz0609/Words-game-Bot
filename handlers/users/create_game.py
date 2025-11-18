import os
import aiofiles
import re
import json

from aiogram import Router, types , F
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton



from data.db_games_functions import get_file_name , save_dates , get_dates_all
from data.db_users_functions import get_user
from keyboards.default.reply_menu import menu_kb
from states.create_game_state import Create_game

router = Router()




#fayl nomi to'gri saqlash uchun funksiya
def make_safe_filename(name: str) -> str:
    """
    Foydalanuvchi kiritgan nomni fayl nomiga moslashtiradi.
    Windows, Linux va macOS uchun xavfsiz.
    """
    name = name.strip()  # bo'shliqlarni olib tashlash
    if not name:
        return None  # bo'sh nom
    # Shuningdek, bo‘shliq bilan tugash yoki nuqta bilan tugashni oldini olish
    name = re.sub(r'[\\/:*?"<>|\0]', "_", name)  
    name = re.sub(r'\s+$', "", name)  # oxirgi bo'sh joylarni olib tashlash
    if not name:
        return None 
    return name

 
  
  
     
# bu router foydalanuvchi "O'yin yaratish"  tugmasini bosganida ishga tushadi
@router.message(F.text == "🧩 Yangi o‘yin yaratish")
async def game_create(message : types.Message , state: FSMContext):
        keyboard = ReplyKeyboardMarkup(
                keyboard=[
                [KeyboardButton(text="🔙 Orqaga")]
            ],
            resize_keyboard=True
            )    
        await message.answer(
            "📝 Iltimos, yangi o‘yinga nom kiriting.\n\nMasalan: <b>Eng_Uzb</b>",
            parse_mode="HTML",
            reply_markup=keyboard
        )

        await state.set_state(Create_game.name_create)




#  bu router foydalanuvchidan yaratmoqchi bo'lgan o'yinini nomini so'raydi va bunday nomli o'yin yaratmagan bo'lsa uni yaratadi
#  keyin bu o'yin malumotlarini ma'lumotlar bazasiga yuboradi va diskda bu o'yin uchun alohida txt fayl yaratiladi
@router.message(Create_game.name_create, F.text)
async def name_create(message : types.Message , state: FSMContext):

    text = message.text.strip()
    if text in ["🔙 Orqaga", "/start"]:
        await message.answer("Bosh sahifa", reply_markup=menu_kb)
        await state.clear()
        return
    
    user_id = message.from_user.id
    name = message.text
    safe_name = make_safe_filename(name)
    
    if not safe_name:
        await message.answer("Siz yozgan nom tizim uchun mos emas . Boshqa nom yozib ko'ring")
        return
    
    #foydalanuvchi oldin bunday nomdagi o'yin yaratganmi yoki yo'qligini tekshiryabmiz
    get_bool = await get_file_name(user_id , name)
    if not get_bool:
        #foydalanuvchiga random tarzda fayl nomini taklif etyabmiz
        keyboard_name = ""
        i = 1
        idic = True
        while idic:
            random_name = f"{name}{i}"
            check = await get_file_name(user_id , random_name)  
            if check:
                keyboard_name = random_name
                idic = False 
            else:
                i+=1
                
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
            [KeyboardButton(text=keyboard_name)]
            ],
            resize_keyboard=True
        )  
        await message.answer(f"⚠️ Bu nomdagi o‘yin allaqachon mavjud.\nIltimos, boshqa nom tanlang yoki pastdagi tugmani bosing." , reply_markup=keyboard)
        return
    
    await message.answer(
        f"✅ <b>{name}</b> nomli yangi o'yin muvaffaqiyatli yaratildi!",
        parse_mode="HTML"
    )

    await message.answer(
        "✍️ Endi so'zlarni ularning tarjimalari bilan birma-bir kiriting.\n\n"
        "<b>Namuna:</b>\n"
        "<code>olma - apple</code>\n"
        "<code>eat out - restoranda ovqatlanish</code>\n"
        "<code>check-in - ro‘yxatdan o‘tish</code>\n\n"
        "Har bir so‘zni yangi qatordan yuboring.",
        parse_mode="HTML"
)

    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
        [KeyboardButton(text="💾 Saqlash va yakunlash")],
        ],
        resize_keyboard=True
    )   
    await message.answer(
        "📦 So'zlarni kiritishni tugatgach, <b>💾 Saqlash va yakunlash</b> tugmasini bosib jarayonni yakunlang.",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    
    # keyingi state ga yuborish uchun malumotlarni saqlash
    await state.update_data(name = name)
    await state.update_data(safe_name = safe_name)
    await state.set_state(Create_game.word_create)
 
 
    
# bu funksiya foydalanuvchi yuborgan so'zlarni diskdagi faylga yozadi
@router.message(Create_game.word_create, F.text)
async def words_input(message: types.Message , state: FSMContext):
    
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
    
    
    if message.text == "💾 Saqlash va yakunlash" or message.text == "/start":
        user_id = message.from_user.id
        
        
        #oldingi router state orqali yuborgan ma'lumotlarni olish
        data = await state.get_data()
        words_dict = data.get("words_dict")
        words_number = data.get("words_number")
        
        if words_number is None:
            words_number = 0
            
        file_name = data.get("name")
        safe_file_name = data.get("safe_name")
        
        #o'yinni yaratuvchisini nomini olyabmiz
        creater_name = await get_user(user_id)
        # foydalanuvchi nomini file uchun moslayabmiz
        save_creater_name = make_safe_filename(creater_name)
        
        # foydalanuvchi o'yin nomini kiritgandan so'ng unga fayl yaratish
        folder = "data/disk"
        os.makedirs(folder, exist_ok=True)  # Papka yo‘q bo‘lsa yaratadi
        f_name = f"{save_creater_name}_{user_id}_{safe_file_name}.json"
        file_path = os.path.join(folder, f_name) 
        
        #foydalanuvchi ma'lumotlarini ma'lumotlar bazasiga saqlash va bu satrninig id raqamini olish
        game_id = await save_dates(user_id , file_name , creater_name , file_path , words_number=words_number )
        
        if not words_dict:
            words_dict = {}
        # asinxron tarzda so'zlarni json fayl ga yozish
        async with aiofiles.open(file_path, mode="w", encoding="utf-8") as f:
            await f.write(json.dumps(words_dict, ensure_ascii=False, indent=4))
        
        url = f"tg://user?id={user_id}"
        text = f"""
        <b>🎮 O'yin ma'lumotlari</b>\n
        👤 <b>Yaratuvchi:</b> <a href="{url}">{creater_name}</a>
        📚 <b>So'zlar soni:</b> {words_number} ta
        📝 <b>O'yin nomi:</b> {file_name}
        🆔 <b>ID:</b> <code>{game_id}</code>
        """
        await message.answer(text, parse_mode="HTML")
        await message.answer(
            "🔗 O'yin ID ni ulashing — boshqalar ham siz yaratgan o'yinga qo'shilishlari mumkin!",
            reply_markup=menu_kb
        )
                
        await state.clear()
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

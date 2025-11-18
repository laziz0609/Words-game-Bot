from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🎮 O‘yin o'ynash"),
            KeyboardButton(text="🧩 Yangi o‘yin yaratish")
        ],
        [
            KeyboardButton(text="📂 Mening o‘yinlarim"),
            KeyboardButton(text="✍️ Ismni yangilash")
        ],
    ],
    resize_keyboard=True
)

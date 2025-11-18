from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

game_or_words = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📚 So'zlar ro'yxati"),
            KeyboardButton(text="🎮 O'yinni boshlash")
        ],
        [
            KeyboardButton(text="🏠 Bosh sahifa")
        ],
    ],
    resize_keyboard=True
)

exit_or_words = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🔙 Orqaga"),
            KeyboardButton(text="⛔ O'yinni to'xtatish")
        ],
    ],
    resize_keyboard=True
)

end_game = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🎮 Yana o‘ynash"),
            KeyboardButton(text="📋 Topilmagan so‘zlar ro‘yxati"),
        ],
        [
            KeyboardButton(text="🏠 Asosiy menyu"),
        ],
    ],
    resize_keyboard=True
)

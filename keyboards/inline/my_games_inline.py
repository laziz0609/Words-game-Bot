from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData
from data.db_games_functions import get_dates_id


class MyGamesCallbackData(CallbackData, prefix="game"):
    game_id: int


# foydalanuvchininig barcha o'yinlarini ko'rsatish tugmalari
async def my_games_button(user_id):
    infos = await get_dates_id(user_id)

    if not infos:
        return False

    buttons = []

    for info in infos:
        game_id = info[0]
        name = info[1]

        buttons.append(
            InlineKeyboardButton(
                text=name,
                callback_data=MyGamesCallbackData(
                    game_id=game_id
                ).pack()
            )
        )
        
    # 2tadan qatorga joylashtirish
    rows = [buttons[i:i+2] for i in range(0, len(buttons), 2)]

    return InlineKeyboardMarkup(inline_keyboard=rows)


game_config = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="📖 So‘zlarni ko‘rish", callback_data="view_words"),
        ],
        [
            InlineKeyboardButton(text="➕ So‘z qo‘shish", callback_data="add_words"),
            InlineKeyboardButton(text="❌ So‘zni o‘chirish", callback_data="delete_words"),
        ],
        [
            InlineKeyboardButton(text="🗑 O‘yinni o‘chirish", callback_data="delete_game"),
        ],
        [
            InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_menu"),
            InlineKeyboardButton(text="🏠 Asosiy menu", callback_data="to_main_menu"),
        ],
    ]
)


# o'yinni o'chirish
delete_game_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Ha, o‘chirilsin", callback_data="confirm_delete_game"),
            InlineKeyboardButton(text="❌ Yo‘q, bekor qilinsin", callback_data="cancel_delete_game"),
        ]
    ]
)
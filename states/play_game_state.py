from aiogram.fsm.state import StatesGroup , State

class Play_Game(StatesGroup):
    id_input = State()
    words_or_game = State()
    game = State()
    game_again = State()
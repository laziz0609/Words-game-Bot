from aiogram.fsm.state import State , StatesGroup

class My_Games(StatesGroup):
    viewing_game = State()
    delate_game = State()
    adding_words = State()
    deleting_words = State()
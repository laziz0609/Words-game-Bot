from aiogram.fsm.state import State , StatesGroup


class Create_game(StatesGroup):
    name_create = State()
    word_create = State()
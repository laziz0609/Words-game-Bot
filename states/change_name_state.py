from aiogram.fsm.state import State , StatesGroup

class Change_name(StatesGroup):
    waiting_for_new_name = State()
from aiogram.fsm.state import State, StatesGroup


class SetStates(StatesGroup):
    waiting_for_max_num = State()
    waiting_for_echo = State()
    waiting_for_yes_or_no = State()
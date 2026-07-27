from aiogram.fsm.state import State, StatesGroup


class SubFSM(StatesGroup):
    city = State()
    min_rooms = State()
    max_price = State()

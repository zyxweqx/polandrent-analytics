from aiogram.fsm.state import State, StatesGroup


class SubscriptionStates(StatesGroup):
    district = State()
    min_price = State()
    max_price = State()
    rooms = State()
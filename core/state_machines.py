from aiogram.fsm.state import StatesGroup, State


class RoutingFsm(StatesGroup):
    none = State()
    getting_url = State()

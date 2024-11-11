from aiogram.fsm.state import StatesGroup, State


class RoutingFsm(StatesGroup):
    '''
    стейт машина используемая для обработки кнопки предсказать результат матча
    '''
    none = State()
    getting_url = State()

from aiogram import Router, F
from aiogram.types.message import Message
from aiogram.types import CallbackQuery
from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from core.state_machines import RoutingFsm

top_level_router = Router()


@top_level_router.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer('привет чтобы вызвать меню напиши /menu')


@top_level_router.message(Command('menu'))
async def menu(message: Message) -> None:

    kb = InlineKeyboardMarkup(
        inline_keyboard=[  # первая строка
            [InlineKeyboardButton(text='Предсказать результат матча', callback_data='predict'),
             InlineKeyboardButton(text='Предсказать лайв матчи', callback_data='live_predict')],
            # вторая строка
            [InlineKeyboardButton(text='Предсказать результаты матчей на сегодня',
                                  callback_data='today_predict'),
                InlineKeyboardButton(text='Предсказать результаты матчей на завтра',
                                     callback_data='tommorow_predict')]])

    await message.answer('reply keyboard', reply_markup=kb)


@top_level_router.callback_query(F.data == 'predict')
async def predict(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await callback.message.answer('введите url матча')
    await state.set_state(RoutingFsm.getting_url)


@top_level_router.callback_query(F.data == 'live_predict')
async def live_predict(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.answer('live_predict')


@top_level_router.callback_query(F.data == 'today_predict')
async def today_predict(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.answer('today_predict')


@top_level_router.callback_query(F.data == 'tommorow_predict')
async def tommorow_predict(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.answer('tommorow_predict')

from aiogram import Router, F
from aiogram.types.message import Message
from aiogram.types import CallbackQuery
from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from core.state_machines import RoutingFsm
from core.predictions import PredictionData

top_level_router = Router()


@top_level_router.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer('привет чтобы вызвать меню напиши /menu')


@top_level_router.message(Command('menu'))
async def menu(message: Message) -> None:

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Предсказать результат матча', callback_data='predict')],
            [InlineKeyboardButton(text='Предсказать лайв матчи', callback_data=PredictionData(date='live').pack())],
            [InlineKeyboardButton(text='Предсказать результаты матчей на сегодня',
                                  callback_data=PredictionData(date='today').pack())],
            [InlineKeyboardButton(text='Предсказать результаты матчей на завтра',
                                  callback_data=PredictionData(date='tomorrow').pack())]])

    await message.answer('reply keyboard', reply_markup=kb)


@top_level_router.callback_query(F.data == 'predict')
async def predict(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await callback.message.answer('введите url матча')
    await state.set_state(RoutingFsm.getting_url)

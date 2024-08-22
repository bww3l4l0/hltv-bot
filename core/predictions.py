import re
import asyncio
import pickle
import logging
from aiogram import Router, F
from aiogram.filters.callback_data import CallbackData
from aiogram.types.message import Message
from core.state_machines import RoutingFsm
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from concurrent.futures import ThreadPoolExecutor
from parser.hltv_parser_extended_data import process_match
from parser.prepocessing import preprocess
from parser.match_url_parser import fetch_match_urls
from pandas import DataFrame
from numpy import ndarray
from textwrap import dedent
from typing import Literal

logger = logging.getLogger(__name__)

pool = ThreadPoolExecutor(2)

prediction_router = Router(name='predictions')


class PredictionData(CallbackData, prefix='123'):
    date: Literal['live', 'today', 'tomorrow']


regex_pattern = re.compile(
    r"^(?:http|ftp)s?://"
    r"(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?$)"
    r"(?::\d+)?"
    r"(?:/?|[/?]\S+)$", re.IGNORECASE)

with open('/home/sasha/Documents/vscode/hltv v2 bot/core/model/hltv_v2_model_dump', 'rb') as file:
    model = pickle.load(file)


def validate_url(url: str) -> bool:
    return re.match(regex_pattern, url) is not None


def make_result_str(data: DataFrame, prediction: ndarray) -> str:
    # round
    result = dedent(f'''url: {data['url'][0]}
{data['t1_name'][0]} : {data['t2_name'][0]}
date: {data['date'][0]}
first team win prob: {round(prediction[0][0], 3)}
second team win prob: {round(prediction[0][1], 3)}
''')
    return result


# рабочая версия но с использованием asyncio
async def process_match_wrapper(url: str, message: Message) -> None:

    event_loop = asyncio.get_running_loop()
    try:
        data = await event_loop.run_in_executor(pool, process_match, url)

    except Exception as e:
        await message.answer(dedent(f'''url: {url}\nневозможно извлечь нужные данные'''))
        logger.exception(e)
        return

    if type(data) is dict:
        try:
            data = preprocess(data)
            prediction = model.predict_proba(data)
            message_text = make_result_str(data, prediction)
            await message.answer(message_text)
            return
        except Exception as e:
            await message.answer(dedent(f'''url; {url}\nневозможно сделать предсказание'''))
            logger.exception(e)


@prediction_router.message(RoutingFsm.getting_url)
async def predict_one(message: Message, state: FSMContext, ) -> None:

    url = message.text

    if not validate_url(url):
        await message.answer('плохая ссылка')
        return

    await state.set_state(RoutingFsm.none)

    await process_match_wrapper(url, message)


@prediction_router.callback_query(PredictionData.filter(F.date.in_(['live', 'today', 'tomorrow'])))
async def predict_some(callback: CallbackQuery, callback_data: PredictionData) -> None:
    await callback.answer()

    event_loop = asyncio.get_running_loop()

    urls = await event_loop.run_in_executor(pool, fetch_match_urls, callback_data.date)

    tasks = [process_match_wrapper(url, callback.message) for url in urls]
    await asyncio.gather(*tasks)


# @prediction_router.callback_query(F.data == 'today_predict')
# #@prediction_router.callback_query(PredictionData.filter(F.data == 'today'))
# async def today_predict(callback: CallbackQuery) -> None:
#     await callback.answer()
#     await callback.message.answer('today_predict')

#     event_loop = asyncio.get_running_loop()

#     urls = await event_loop.run_in_executor(pool, fetch_match_urls, 'today')

#     await callback.message.answer(str(urls))

#     tasks = []
#     for url in urls:
#         print(url)
#         tasks.append(event_loop.create_task(process_match_wrapper(url, callback.message)))
#     await tasks


# @prediction_router.callback_query(F.data == 'tommorow_predict')
# async def tommorow_predict(callback: CallbackQuery) -> None:
#     await callback.answer()
#     await callback.message.answer('tommorow_predict')

#     event_loop = asyncio.get_running_loop()

#     urls = await event_loop.run_in_executor(pool, fetch_match_urls, 'tomorrow')

#     await callback.message.answer(str(urls))

#     tasks = []
#     for url in urls:
#         print(url)
#         tasks.append(event_loop.create_task(process_match_wrapper(url, callback.message)))
#     # await tasks
#     await asyncio.gather(*tasks)

'''TO DO
рефакторинг в 1 хендлер
'''

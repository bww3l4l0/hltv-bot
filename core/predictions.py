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
from pandas import DataFrame
from numpy import ndarray, around
from textwrap import dedent
from typing import Literal
from celery.result import AsyncResult
from parser.prepocessing import preprocess
from celery_tasks import process_match_task, fetch_match_urls_task

logger = logging.getLogger(__name__)

prediction_router = Router(name='predictions')


class PredictionData(CallbackData, prefix='123'):
    date: Literal['live', 'today', 'tomorrow']


regex_pattern = re.compile(
    r"^(?:http|ftp)s?://"
    r"(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?$)"
    r"(?::\d+)?"
    r"(?:/?|[/?]\S+)$", re.IGNORECASE)

url_pattern = re.compile('https://www.hltv.org/matches/\\d{5,7}/\\S{20,300}')

with open('/home/sasha/Documents/vscode/hltv v2 bot/core/model/hltv_v2_model_dump', 'rb') as file:
    model = pickle.load(file)


def validate_url(url: str) -> bool:
    return re.match(url_pattern, url) is not None


def make_result_str(data: DataFrame, prediction: ndarray) -> str:
    result = dedent(f'''url: {data['url'][0]}
{data['t1_name'][0]} : {data['t2_name'][0]}
date: {data['date'][0]}
first team win prob: {prediction[0][0]:.3f}
second team win prob: {prediction[0][1]:.3f}
''')
    return result


async def wait_task_result(result_object: AsyncResult) -> any:
    while True:
        await asyncio.sleep(10)
        if result_object.ready():
            return result_object.result


# рабочая версия но с использованием asyncio
async def process_match_wrapper(url: str, message: Message) -> None:

    result_object = process_match_task.apply_async((url,), queue='xyz')
    data = await wait_task_result(result_object)

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

    else:
        await message.answer(dedent(f'''url: {url}\nневозможно извлечь нужные данные'''))
        logger.exception(data)
        return


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

    result_object = fetch_match_urls_task.apply_async((callback_data.date,), queue='xyz')

    urls = await wait_task_result(result_object)

    tasks = [process_match_wrapper(url, callback.message) for url in urls]
    await asyncio.gather(*tasks)

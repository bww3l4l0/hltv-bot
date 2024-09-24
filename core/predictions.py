import re
import asyncio
import pickle
import logging
import json
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types.message import Message
from core.state_machines import RoutingFsm
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from pandas import DataFrame
from numpy import ndarray
from textwrap import dedent
from typing import Literal, Callable, Awaitable
from celery.result import AsyncResult

from parser.prepocessing import preprocess
from celery_tasks import (process_match_task,
                          fetch_match_urls_task,
                          app as celery_app)
from redis import Redis

from settings import settings

# SLEEP_TIME = 10
logger = logging.getLogger(__name__)

prediction_router = Router(name='predictions')

tasks = set()


class PredictionData(CallbackData, prefix='123'):
    date: Literal['live', 'today', 'tomorrow']


regex_pattern = re.compile(
    r"^(?:http|ftp)s?://"
    r"(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?$)"
    r"(?::\d+)?"
    r"(?:/?|[/?]\S+)$", re.IGNORECASE)


with open('/home/sasha/Documents/vscode/hltv v2 bot/core/model/hltv_v2_model_dump', 'rb') as file:
    model = pickle.load(file)

url_pattern = re.compile('https://www.hltv.org/matches/\\d{5,7}/\\S{20,300}')


def validate_url(url: str) -> bool:
    '''url validation for predict one'''
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
        await asyncio.sleep(settings.ASYNCIO_SLEEP_TIME)
        if result_object.ready():
            return result_object.result


async def wrap_task(coro: Callable[..., Awaitable]) -> None:
    task = asyncio.create_task(coro)
    tasks.add(task)
    try:
        await task
    except asyncio.CancelledError:
        tasks.remove(task)
        return
    tasks.remove(task)


# рабочая версия но с использованием asyncio
async def process_match(url: str, message: Message, redis: Redis) -> None:

    # check redis by url
    # хранить будем сообщения на ответ с ttl 3600
    data = redis.get(url)

    # сериализация ошибки
    # попробовать поймать ошибку извлечения данных
    if data is None:
        result_object = process_match_task.apply_async((url,), queue='xyz')
        data = await wait_task_result(result_object)
        if type(data) is dict:
            msg = json.dumps(data)
            redis.setex(url, settings.REDIS_CACHE_TTL, msg)
        else:
            redis.setex(url, settings.REDIS_CACHE_TTL, 'Exception')

    elif data == b'Exception':
        data = None
    else:
        data = json.loads(data)

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


@prediction_router.message(Command('cancel'))
async def calcel(message: Message) -> None:
    await message.answer('задачи отменены')
    for task in tasks:
        task.cancel()
    celery_app.control.purge()
    # celery -A proj purge -Q queue1,queue2


@prediction_router.message(RoutingFsm.getting_url)
async def predict_one(message: Message, state: FSMContext, redis: Redis) -> None:

    url = message.text

    if not validate_url(url):
        await message.answer('плохая ссылка')
        return

    await state.set_state(RoutingFsm.none)

    # await process_match(url, message, redis)
    await wrap_task(process_match(url, message, redis))


@prediction_router.callback_query(PredictionData.filter(F.date.in_(['live', 'today', 'tomorrow'])))
async def predict_some(callback: CallbackQuery, callback_data: PredictionData, redis: Redis) -> None:
    await callback.answer()

    result_object = fetch_match_urls_task.apply_async((callback_data.date,), queue='xyz')

    urls = await wait_task_result(result_object)

    tasks = [wrap_task(process_match(url, callback.message, redis)) for url in urls]
    await asyncio.gather(*tasks)

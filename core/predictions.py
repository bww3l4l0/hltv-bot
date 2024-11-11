import re
import asyncio
import pickle
import logging
import json
from aiogram import Router, F, Bot
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

from redis.asyncio import Redis

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


with open('./core/model/hltv_v2_model_dump', 'rb') as file:
    model = pickle.load(file)

url_pattern = re.compile('https://www.hltv.org/matches/\\d{5,7}/\\S{20,300}')


def validate_url(url: str) -> bool:
    '''валидация url передаваемого при обработки кнопки предсказать матч'''
    return re.match(url_pattern, url) is not None


def make_result_str(data: DataFrame, prediction: ndarray) -> str:
    '''
    формирует строку результат для отправки сообщения
    '''
    result = dedent(f'''{data['t1_name'][0]} : {data['t2_name'][0]}
url: {data['url'][0]}
date: {data['date'][0]}
first team win prob: {prediction[0][0]:.3f}
min coef for profit: {(1 / (prediction[0][0] - settings.CORRECTION)):.3f}
second team win prob: {prediction[0][1]:.3f}
min coef for profit: {(1 / (prediction[0][1] - settings.CORRECTION)):.3f}
''')
    return result


async def wait_task_result(result_object: AsyncResult) -> any:
    '''
    обертка позволяющая селери работать в асинхронном контексте
    '''
    while True:
        await asyncio.sleep(settings.ASYNCIO_SLEEP_TIME)
        if result_object.ready():
            return result_object.result


async def wrap_task(coro: Callable[..., Awaitable]) -> None:
    '''
    обертка над корутиной, для поддержания списка активных задач
    '''
    task = asyncio.create_task(coro)
    tasks.add(task)
    try:
        await task
    except asyncio.CancelledError:
        tasks.remove(task)
        return
    tasks.remove(task)


async def process_match(url: str,
                        bot: Bot,
                        user_id: int,
                        redis: Redis
                        ) -> None:
    '''
    обработка матча по url и отправка сообщения пользователю
    '''

    data = await redis.get(url)

    if data is None:
        result_object = process_match_task.apply_async((url,), queue=settings.CELERY_QUEUE_NAME)
        data = await wait_task_result(result_object)

        if type(data) is dict:
            msg = json.dumps(data)

            await redis.setex(url, settings.REDIS_CACHE_TTL, msg)
        else:
            await redis.setex(url, settings.REDIS_CACHE_TTL, 'Exception')

    elif data == b'Exception':
        data = None
        await bot.send_message(user_id, dedent(f'''url; {url}\nневозможно сделать предсказание'''))

    # elif data[:3] == b'{"':
    #     data = json.loads(data)

    else:  # получается есть готовый предикт
        await bot.send_message(user_id, data)
        return

    if type(data) is dict:
        try:

            data = preprocess(data)
            prediction = model.predict_proba(data)
            message_text = make_result_str(data, prediction)
            await redis.setex(url, settings.REDIS_CACHE_TTL, message_text)
            await bot.send_message(user_id, message_text)
            return
        except Exception as e:

            await redis.setex(url, settings.REDIS_CACHE_TTL, 'Exception')
            await bot.send_message(user_id, dedent(f'''url: {url}\nневозможно сделать предсказание'''))
            logging.exception(e)

    else:
        await bot.send_message(user_id, dedent(f'''url: {url}\nневозможно извлечь нужные данные'''))
        logging.exception(data)
        return


@prediction_router.message(Command('cancel'))
async def calcel(message: Message) -> None:
    '''
    отмена задач находящихся в tasks
    '''
    await message.answer('задачи отменены')
    for task in tasks:
        task.cancel()
    celery_app.control.purge()
    # celery -A proj purge -Q queue1,queue2


@prediction_router.message(RoutingFsm.getting_url)
async def predict_one(message: Message, bot: Bot, state: FSMContext, redis: Redis) -> None:
    '''
    обработка одного матча
    '''

    url = message.text

    if not validate_url(url):
        await message.answer('плохая ссылка')
        return

    await state.set_state(RoutingFsm.none)

    # await process_match(url, message, redis)
    await wrap_task(process_match(url, bot, message.chat.id, redis))


@prediction_router.callback_query(PredictionData.filter(F.date.in_(['live', 'today', 'tomorrow'])))
async def predict_some(callback: CallbackQuery, callback_data: PredictionData, bot: Bot, redis: Redis) -> None:
    '''
    обработка нескольких матчей
    '''
    await callback.answer()

    result_object = fetch_match_urls_task.apply_async((callback_data.date,), queue=settings.CELERY_QUEUE_NAME)

    urls = await wait_task_result(result_object)

    callback.message

    print(urls)

    tasks = [wrap_task(process_match(url, bot, callback.message.chat.id, redis)) for url in urls]
    await asyncio.gather(*tasks)

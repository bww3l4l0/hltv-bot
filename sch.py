import asyncio
import logging
import pickle
import json

from textwrap import dedent

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.triggers.cron import CronTrigger
from aiogram import Bot
# from redis import Redis
from redis.asyncio.connection import ConnectionPool
from redis.asyncio import Redis

from celery_tasks import process_match_task, fetch_match_urls_task
from core.predictions import wait_task_result, make_result_str, process_match
from parser.prepocessing import preprocess

from settings import settings


with open('./core/model/hltv_v2_model_dump', 'rb') as file:
    model = pickle.load(file)

users = [{
    'telegram_id': 993955495,
    'autopredict_next_day': True
}]


# async def process_match(url: str,
#                         bot: Bot,
#                         user_id: int,
#                         redis: Redis
#                         ) -> None:

#     data = await redis.get(url)

#     if data is None:
#         result_object = process_match_task.apply_async((url,), queue=settings.CELERY_QUEUE_NAME)
#         data = await wait_task_result(result_object)

#         if type(data) is dict:
#             msg = json.dumps(data)

#             await redis.setex(url, settings.REDIS_CACHE_TTL, msg)
#         else:
#             await redis.setex(url, settings.REDIS_CACHE_TTL, 'Exception')

#     elif data == b'Exception':
#         data = None
#     else:
#         data = json.loads(data)

#     if type(data) is dict:
#         try:

#             data = preprocess(data)
#             prediction = model.predict_proba(data)
#             message_text = make_result_str(data, prediction)
#             await redis.setex(url, message_text, settings.REDIS_CACHE_TTL)
#             await bot.send_message(user_id, message_text)
#             return
#         except Exception as e:

#             await bot.send_message(user_id, dedent(f'''url; {url}\nневозможно сделать предсказание'''))
#             logging.exception(e)

#     elif type(data) is str:  # вслучае если есть готовый предикт
#         await bot.send_message(user_id, data)
#         return

#     else:
#         await bot.send_message(user_id, dedent(f'''url: {url}\nневозможно извлечь нужные данные'''))
#         logging.exception(data)
#         return


async def process_tomorrow_predictions(bot: Bot, redis: Redis) -> None:
    '''
    Предсказывает результаты матчей следующего дня
    '''

    # выбираем всех пользователей которые подписаны на рассылку
    users = await redis.smembers('bot_subscribers')

    # получаем ссылки на завтрашние матчи
    task_obj = fetch_match_urls_task.apply_async(('tomorrow',), queue='xyz')
    match_urls_list = await wait_task_result(task_obj)

    if not match_urls_list:
        return

    # создаем корутины
    tasks = [process_match(url, bot, user, redis)
             for url in match_urls_list
             for user in users]

    print('tasks')
    print(tasks)

    await asyncio.gather(*tasks)


def run_scheduler(bot: Bot) -> None:

    # if users[0]['autopredict_next_day']:

        # bot = Bot(token=settings.TOKEN)

    # redis_pool = ConnectionPool(settings.REDIS_DSN)
    redis_pool = ConnectionPool(host=settings.REDIS_DSN.host,
                                port=settings.REDIS_DSN.port,
                                db=settings.REDIS_DSN.path[1:])

    redis_conn = Redis(connection_pool=redis_pool)

    executors = {
        'default': AsyncIOExecutor()
    }
    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)
    scheduler = AsyncIOScheduler(executors=executors)
    cron = CronTrigger(hour=settings.AUTOPREDICT_CRON_HOUR,
                       minute=settings.AUTOPREDICT_CRON_MINUTE)
    scheduler.add_job(process_tomorrow_predictions, cron, (bot, redis_conn))  # cron
    scheduler.start()
    asyncio.get_event_loop().run_forever()


logging.basicConfig(
    format='[%(filename)s:%(lineno)d] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('./.logs/apscheduler.log')],
    level=logging.DEBUG
    )
# logging.getLogger('apscheduler').setLevel(logging.DEBUG)

# triger_time = datetime.now() + timedelta(seconds=15)
# scheduler.add_job(process_tomorrow_predictions, 'date', run_date=triger_time)  # cron


if __name__ == '__main__':
    bot = Bot(token=settings.BOT_TOKEN.get_secret_value())
    run_scheduler(bot)


# asyncio.run(process_tomorrow_predictions())

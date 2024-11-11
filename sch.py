import asyncio
import logging
import pickle

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.triggers.cron import CronTrigger
from aiogram import Bot
# from redis import Redis
from redis.asyncio.connection import ConnectionPool
from redis.asyncio import Redis

from celery_tasks import fetch_match_urls_task
from core.predictions import wait_task_result, process_match

from settings import settings


with open('./core/model/hltv_v2_model_dump', 'rb') as file:
    model = pickle.load(file)

users = [{
    'telegram_id': 993955495,
    'autopredict_next_day': True
}]


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

    redis_pool = ConnectionPool(host=settings.REDIS_DSN.host,
                                port=settings.REDIS_DSN.port,
                                db=settings.REDIS_DSN.path[1:])

    redis_conn = Redis(connection_pool=redis_pool)

    executors = {
        'default': AsyncIOExecutor()
    }

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


if __name__ == '__main__':
    bot = Bot(token=settings.BOT_TOKEN.get_secret_value())
    run_scheduler(bot)

import asyncio
import logging
import pickle

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.triggers.cron import CronTrigger
from aiogram import Bot

from celery_tasks import process_match_task, fetch_match_urls_task
from core.predictions import wait_task_result, make_result_str
from parser.prepocessing import preprocess

from settings import settings


with open('./core/model/hltv_v2_model_dump', 'rb') as file:
    model = pickle.load(file)

users = [{
    'telegram_id': 993955495,
    'autopredict_next_day': True
}]


async def process_match(url: str,
                        bot: Bot,
                        user_id: int
                        ) -> None:
    '''
    Обрабатывает 1 матч
    '''
    task_obj = process_match_task.apply_async((url,), queue='xyz')
    match_data = await wait_task_result(task_obj)
    if type(match_data) is dict:
        match_data = preprocess(match_data)
        predictions = model.predict_proba(match_data)
        result_str = make_result_str(match_data, predictions)
        await bot.send_message(user_id, result_str)


async def process_tomorrow_predictions(bot: Bot) -> None:
    '''
    Предсказывает результаты матчей следующего дня
    '''

    task_obj = fetch_match_urls_task.apply_async(('tomorrow',), queue='xyz')
    match_urls_list = await wait_task_result(task_obj)
    if not match_urls_list:
        return

    tasks = [process_match(url, bot, users[0]['telegram_id']) for url in match_urls_list]

    await asyncio.gather(*tasks)


def run_scheduler(bot: Bot) -> None:
    if users[0]['autopredict_next_day']:

        # bot = Bot(token=settings.TOKEN)

        executors = {
            'default': AsyncIOExecutor()
        }
        # loop = asyncio.new_event_loop()
        # asyncio.set_event_loop(loop)
        scheduler = AsyncIOScheduler(executors=executors)
        cron = CronTrigger(hour=settings.AUTOPREDICT_CRON_HOUR,
                           minute=settings.AUTOPREDICT_CRON_MINUTE)
        scheduler.add_job(process_tomorrow_predictions, cron, (bot,))  # cron
        scheduler.start()
        asyncio.get_event_loop().run_forever()


logging.basicConfig(handlers=[
    logging.StreamHandler(),
    logging.FileHandler('apscheduler.log')
    ],
    level=logging.DEBUG
    )
# logging.getLogger('apscheduler').setLevel(logging.DEBUG)

# triger_time = datetime.now() + timedelta(seconds=15)
# scheduler.add_job(process_tomorrow_predictions, 'date', run_date=triger_time)  # cron


if __name__ == '__main__':
    bot = Bot(token=settings.TOKEN)
    run_scheduler(bot)


# asyncio.run(process_tomorrow_predictions())

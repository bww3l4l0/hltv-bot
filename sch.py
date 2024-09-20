import os
import asyncio
import logging
import pickle

from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.executors.asyncio import AsyncIOExecutor
from aiogram import Bot

from celery_tasks import process_match_task, fetch_match_urls_task
from core.predictions import wait_task_result, make_result_str
from parser.prepocessing import preprocess
from settings import settings


with open('/home/sasha/Documents/vscode/hltv v2 bot/core/model/hltv_v2_model_dump', 'rb') as file:
    model = pickle.load(file)


async def process_match(url: str, bot: Bot) -> None:
    task_obj = process_match_task.apply_async((url,), queue='xyz')
    match_data = await wait_task_result(task_obj)
    if type(match_data) is dict:
        match_data = preprocess(match_data)
        predictions = model.predict_proba(match_data)
        result_str = make_result_str(match_data, predictions)
        await bot.send_message(settings.TELEGRAM_ID, result_str)


async def process_tomorrow_predictions(bot: Bot) -> None:

    task_obj = fetch_match_urls_task.apply_async(('tomorrow',), queue='xyz')
    match_urls_list = await wait_task_result(task_obj)
    if not match_urls_list:
        return

    tasks = [process_match(url, bot) for url in match_urls_list]

    await asyncio.gather(*tasks)


def run_scheduler(bot: Bot) -> None:
    if settings.AUTOPREDICT_NEXT_DAY:

        # bot = Bot(token=settings.TOKEN)

        executors = {
            'default': AsyncIOExecutor()
        }
        # loop = asyncio.new_event_loop()
        # asyncio.set_event_loop(loop)
        scheduler = AsyncIOScheduler(executors=executors)
        scheduler.add_job(process_tomorrow_predictions, settings.AUTOPREDICT_CRON, (bot,))  # cron
        scheduler.start()
        asyncio.get_event_loop().run_forever()


logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.DEBUG)

# triger_time = datetime.now() + timedelta(seconds=15)
# scheduler.add_job(process_tomorrow_predictions, 'date', run_date=triger_time)  # cron


if __name__ == '__main__':
    bot = Bot(token=settings.TOKEN)
    run_scheduler(bot)


# asyncio.run(process_tomorrow_predictions())

from random import choice
from celery import Celery

from parser.custom_chrome import process_match, fetch_match_urls
from typing import Literal
from settings import settings


app = Celery('tasks',
             broker=str(settings.REDIS_DSN),
             backend=str(settings.REDIS_DSN))


@app.task()
def fetch_match_urls_task(time: Literal['live', 'today', 'tomorrow']) -> list[str]:
    '''
    таска для извлечения ссылок
    '''
    return fetch_match_urls(time)


@app.task()
def process_match_task(url: str) -> dict[str, any]:
    '''
    таска для извлечения данных матча
    '''
    try:
        return process_match(url, choice(settings.PROXIES))
    except Exception as e:
        return e

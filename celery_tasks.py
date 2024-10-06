from random import choice
from celery import Celery
# from parser.match_url_parser import fetch_match_urls
# from parser.hltv_parser_extended_data import process_match
from parser.custom_chrome import process_match, fetch_match_urls
from typing import Literal
from settings import settings

redis_url = f'''redis://{settings.REDIS_POOL_SETTINGS['host']}:{settings.REDIS_POOL_SETTINGS['port']}/'''

app = Celery('tasks',
             broker=redis_url,
             backend=redis_url)


@app.task()
def fetch_match_urls_task(time: Literal['live', 'today', 'tomorrow']) -> list[str]:
    return fetch_match_urls(time)


@app.task()
def process_match_task(url: str) -> dict[str, any]:
    try:
        return process_match(url, choice(settings.PROXIES))
    except Exception as e:
        return e

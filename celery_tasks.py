from celery import Celery
from parser.match_url_parser import fetch_match_urls
from parser.hltv_parser_extended_data import process_match
# from parser.custom_chrome import process_match
from typing import Literal


app = Celery('tasks',
             broker='redis://localhost:6379/',
             backend='redis://localhost:6379/')


@app.task()
def fetch_match_urls_task(time: Literal['live', 'today', 'tomorrow']) -> list[str]:
    return fetch_match_urls(time)


@app.task()
def process_match_task(url: str) -> dict[str, any]:
    try:
        return process_match(url)
    except Exception as e:
        return e

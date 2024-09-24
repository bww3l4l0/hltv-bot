import os
import shutil
import json
from json import load
from dataclasses import dataclass
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv


load_dotenv()

with open('proxies.json', 'r') as file:
    proxies = json.load(file)


@dataclass(frozen=True, slots=True)
class Settings():
    # AUTOPREDICT_NEXT_DAY: bool = True
    AUTOPREDICT_CRON: CronTrigger = CronTrigger(hour=23,
                                                minute=50)
    # TELEGRAM_ID: int = 993955495
    TOKEN: str = os.getenv('TOKEN')
    REDIS_POOL_SETTINGS = {'host': 'localhost',
                           'port': 6379,
                           'db': 0,
                           'max_connections': 4}
    LOGGING_SETTINGS = {}
    ASYNCIO_SLEEP_TIME = 10
    REDIS_CACHE_TTL = 3600
    PROXIES = proxies


settings = Settings()

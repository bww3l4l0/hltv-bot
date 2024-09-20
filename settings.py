import os
from dataclasses import dataclass
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv

load_dotenv()

# TOKEN = os.getenv('TOKEN')


@dataclass(frozen=True, slots=True)
class Settings():
    AUTOPREDICT_NEXT_DAY: bool = True
    AUTOPREDICT_CRON: CronTrigger = CronTrigger(hour=15,
                                                minute=53)
    TELEGRAM_ID: int = 993955495
    TOKEN: str = os.getenv('TOKEN')
    REDIS_POOL_SETTINGS = {'host': 'localhost',
                           'port': 6379,
                           'db': 0,
                           'max_connections': 4}
    LOGGING_SETTINGS = {}


settings = Settings()

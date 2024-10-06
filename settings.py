import json
from dataclasses import dataclass
from os import getenv
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv


load_dotenv()

with open('proxies.json', 'r') as file:
    proxies = json.load(file)


@dataclass(frozen=True, slots=True)
class Settings():

    AUTOPREDICT_CRON_HOUR = int(getenv('AUTOPREDICT_CRON_HOUR'))
    AUTOPREDICT_CRON_MINUTE = int(getenv('AUTOPREDICT_CRON_MINUTE'))
    ADMIN_ID: int = int(getenv('ADMIN_ID'))
    TOKEN: str = getenv('TOKEN')
    REDIS_POOL_SETTINGS = {'host': getenv('REDIS_POOL_HOST'),
                           'port': getenv('REDIS_POOL_PORT'),
                           'max_connections': int(getenv('REDIS_POOL_MAX_CONNECTIONS'))}

    LOGGING_SETTINGS = {}
    ASYNCIO_SLEEP_TIME: int = int(getenv('ASYNCIO_SLEEP_TIME'))
    REDIS_CACHE_TTL: int = int(getenv('REDIS_CACHE_TTL'))
    PROXIES = proxies
    CHROME_EXECUTABLE_PATH = getenv('CHROME_EXECUTABLE_PATH')
    DRIVER_EXECUTABLE_PATH = getenv('DRIVER_EXECUTABLE_PATH')


settings = Settings()

# print(settings.REDIS_POOL_SETTINGS)

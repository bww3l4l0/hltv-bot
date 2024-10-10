import json
from dataclasses import dataclass
from os import getenv
from apscheduler.triggers.cron import CronTrigger
from pydantic_settings import BaseSettings
from pydantic import Field, NonNegativeFloat
# from pydantic_settings
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
                           'port': getenv('REDIS_POOL_PORT')}
    # PG_POOL_SETTINGS = {'pg_host': getenv('POSTGRESS_HOST'),
    #                     'pg_user': getenv('POSTGRESS_USER'),
    #                     'pg_password': getenv('POSTGRESS_PASSWORD'),
    #                     'pg_pool_size': int(getenv('POSTGRESS_POOL_SIZE')),
    #                     'pg_db_name': getenv('POSTGRESS_DB_NAME')}
    CELERY_QUEUE_NAME: str = getenv('CELERY_QUEUE_NAME')
    LOGGING_SETTINGS = {}
    ASYNCIO_SLEEP_TIME: int = int(getenv('ASYNCIO_SLEEP_TIME'))
    REDIS_CACHE_TTL: int = int(getenv('REDIS_CACHE_TTL'))
    PROXIES = proxies
    CHROME_EXECUTABLE_PATH = getenv('CHROME_EXECUTABLE_PATH')
    DRIVER_EXECUTABLE_PATH = getenv('DRIVER_EXECUTABLE_PATH')
    CORRECTION = float(getenv('CORRECTION'))


# class WebhookSettings(BaseSettings):
#     WEB_SERVER_HOST 
#     WEB_SERVER_PORT
#     BASE_WEBHOOK_URL
#     WEBHOOK_PATH
#     WEBHOOK_SECRET


# webhook_settings = WebhookSettings()


settings = Settings()
# print(settings.PG_POOL_SETTINGS)

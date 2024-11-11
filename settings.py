import json
from os import getenv
from typing import Union
from dotenv import load_dotenv
from pydantic import Field, SecretStr, RedisDsn, FilePath
from pydantic_settings import BaseSettings

load_dotenv(override=True)

with open('proxies.json', 'r') as file:
    proxies = json.load(file)


class Settings(BaseSettings):
    BOT_TOKEN: SecretStr = SecretStr(getenv('TOKEN'))
    ADMIN_ID: int = Field(getenv('ADMIN_ID'), ge=100000, le=10000000000)
    AUTOPREDICT_CRON_HOUR: int = Field(getenv('AUTOPREDICT_CRON_HOUR'), ge=0, lt=24)
    AUTOPREDICT_CRON_MINUTE: int = Field(getenv('AUTOPREDICT_CRON_MINUTE'), ge=0, lt=59)
    ASYNCIO_SLEEP_TIME: int = Field(getenv('ASYNCIO_SLEEP_TIME'), gt=0, le=60)
    REDIS_CACHE_TTL: int = Field(3600, gt=60, le=24000)
    REDIS_DSN: RedisDsn = getenv('REDIS_DSN')
    CELERY_QUEUE_NAME: str = Field(getenv('CELERY_QUEUE_NAME'), min_length=1, max_length=15)
    СELERY_TIMEOUT: int = Field(int(getenv('CELERY_TIMEOUT')), ge=100, le=3600)
    CHROME_EXECUTABLE_PATH: str = getenv('CHROME_EXECUTABLE_PATH')
    DRIVER_EXECUTABLE_PATH: str = getenv('DRIVER_EXECUTABLE_PATH')
    CORRECTION: float = Field(getenv('CORRECTION'), ge=0.001, le=0.1)
    PROXIES: list[Union[str, None]] = proxies
    LOGGING_LEVEL: int = getenv('LOGGING_LEVEL')
    LOGGING_MOD: str = Field(getenv('LOGGING_LEVEL'), min_length=1, max_length=1)  # сделать literal

    class Config:
        frozen = True


# LOGGING_SETTINGS = {}
# PROXIES = proxies

settings = Settings()


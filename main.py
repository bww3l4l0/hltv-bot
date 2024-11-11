import asyncio
import logging
from redis.asyncio import Redis
from redis.asyncio.connection import ConnectionPool

from aiogram import Bot, Dispatcher

from core.menu import top_level_router
from core.predictions import prediction_router
from core.newsleter import newsleter_router
from settings import settings


dispatcher = Dispatcher()


pool = ConnectionPool(host=settings.REDIS_DSN.host,
                      port=settings.REDIS_DSN.port,
                      db=settings.REDIS_DSN.path[1:])

redis_conn = Redis(connection_pool=pool)

dispatcher['redis'] = redis_conn


logging.basicConfig(handlers=[
    logging.FileHandler(filename='./.logs/hltv_v2_log.log', mode=settings.LOGGING_MOD),
    logging.StreamHandler()
    ],
    level=settings.LOGGING_LEVEL
    )

routers = [top_level_router,
           prediction_router,
           newsleter_router]

dispatcher.include_routers(*routers)


async def main() -> None:
    '''
    entry point
    '''
    bot = Bot(settings.BOT_TOKEN.get_secret_value())

    await dispatcher.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())


# требования

# логгинг настройка
# вебхук

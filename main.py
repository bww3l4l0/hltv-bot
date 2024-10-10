import asyncio
import logging
import redis
from redis.asyncio import Redis
from redis.asyncio.connection import ConnectionPool

from aiogram import Bot, Dispatcher
from asyncpg.pool import create_pool

from core.menu import top_level_router
from core.predictions import prediction_router
from core.newsleter import newsleter_router
from settings import settings

# from sch import run_scheduler


# load_dotenv()

# TOKEN = os.getenv('TOKEN')

dispatcher = Dispatcher()

# pool = redis.ConnectionPool(host='localhost', port=6379, db=0, max_connections=4)
pool = ConnectionPool(**settings.REDIS_POOL_SETTINGS)
redis_conn = Redis(connection_pool=pool)

dispatcher['redis'] = redis_conn

# logger = logging.getLogger(__name__)
logging.basicConfig(handlers=[
    logging.FileHandler(filename='./.logs/hltv_v2_log.log', mode='w'),
    logging.StreamHandler()
    ],
    level=logging.INFO
    )

routers = [top_level_router,
           prediction_router,
           newsleter_router]

dispatcher.include_routers(*routers)


async def main() -> None:
    '''
    main method
    '''
    # pg_dsn = f'postgresql://{settings.PG_POOL_SETTINGS['pg_user']}:{settings.PG_POOL_SETTINGS['pg_password']}@{settings.PG_POOL_SETTINGS['pg_host']}'
    # pg_pool = await create_pool(pg_dsn)
    # dispatcher['pg'] = pg_pool
    bot = Bot(settings.TOKEN)
    # process = Process(target=run_scheduler, args=(bot, ))
    # process.start()
    await dispatcher.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())


# требования

# матчинг
# переписать настройки
# добавить бэкап редиса
# вебхук

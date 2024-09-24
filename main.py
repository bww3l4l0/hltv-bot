import os
import asyncio
import logging
import redis

from multiprocessing import Process
from threading import Thread
# from dotenv import load_dotenv
from aiogram import Bot, Dispatcher

from core.menu import top_level_router
from core.predictions import prediction_router
from settings import settings

# from sch import run_scheduler


# load_dotenv()

# TOKEN = os.getenv('TOKEN')

dispatcher = Dispatcher()

# pool = redis.ConnectionPool(host='localhost', port=6379, db=0, max_connections=4)
pool = redis.ConnectionPool(**settings.REDIS_POOL_SETTINGS)
redis_conn = redis.Redis(connection_pool=pool)

dispatcher['redis'] = redis_conn

logger = logging.getLogger(__name__)
logging.basicConfig(filename='hltv_v2_log.log', filemode='w')

routers = [top_level_router,
           prediction_router]

dispatcher.include_routers(*routers)


async def main() -> None:
    '''
    main method
    '''
    bot = Bot(settings.TOKEN)
    # process = Process(target=run_scheduler, args=(bot, ))
    # process.start()
    await dispatcher.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())


# требования
# cancel
# пофиксить 8 разовое создание прокси(создавать прокси из файла 1 раз при запуске бота и не импортировать никуда их(создать константу с проксями)) вынести в баш скрипт
# перенести настройки на pydantic
# изменение настроек через бота
# деплой в докер контейнер
# вебхук
# добавить автоматический обход сайта и оповещение об изменении результата по матчу(опционально)
# добавить аналитику(где данные собираются за последнее время, делаются предикты и считается точность в нескольких показателях)
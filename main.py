import os
import asyncio
import logging
import redis
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from core.menu import top_level_router
from core.predictions import prediction_router


load_dotenv()

TOKEN = os.getenv('TOKEN')

dispatcher = Dispatcher()

pool = redis.ConnectionPool(host='localhost', port=6379, db=0, max_connections=4)
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
    bot = Bot(TOKEN)
    await dispatcher.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())


# требования
# Функции предикт и предикт лайв день завтра
# Кэш(мб через редис) или aiocache может встроить в селери может сделать рефакторинг
# cancel
# добавить прокси
# добавить автоматический обход сайта и оповещение об изменении результата по матчу(опционально)

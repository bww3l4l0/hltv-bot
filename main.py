import asyncio
import logging
import redis

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

# logger = logging.getLogger(__name__)
logging.basicConfig(handlers=[
    logging.FileHandler(filename='hltv_v2_log.log', mode='w'),
    logging.StreamHandler()
    ],
    level=logging.DEBUG
    )

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

# переписать шедулер для многопользовательского режима(запрос тех у кого автопредикт, парсинг, формирование сообщений, рассылка)
# перенести настройки на pydantic
# и переделать на импорт класса
# изменение настроек через бота
# сделать отмену задач в селери
# деплой в докер контейнер
# вебхук
# добавить автоматический обход сайта и оповещение об изменении результата по матчу(опционально)
# добавить аналитику(где данные собираются за последнее время, делаются предикты и считается точность в нескольких показателях)
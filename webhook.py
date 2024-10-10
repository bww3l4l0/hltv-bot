import asyncio
import logging
import redis

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

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


# async def main() -> None:
#     '''
#     main method
#     '''
#     bot = Bot(settings.TOKEN)
#     # process = Process(target=run_scheduler, args=(bot, ))
#     # process.start()
#     await dispatcher.start_polling(bot)

async def on_startup(bot: Bot) -> None:
    # If you have a self-signed SSL certificate, then you will need to send a public
    # certificate to Telegram
    await bot.set_webhook(f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}", secret_token=WEBHOOK_SECRET)


def main() -> None:
    dispatcher = Dispatcher()

    pool = redis.ConnectionPool(**settings.REDIS_POOL_SETTINGS)
    redis_conn = redis.Redis(connection_pool=pool)

    dispatcher['redis'] = redis_conn

    routers = [top_level_router,
               prediction_router]

    dispatcher.include_routers(*routers)

    dispatcher.startup.register(on_startup)

    logging.basicConfig(handlers=[
        logging.FileHandler(filename='hltv_v2_log.log', mode='w'),
        logging.StreamHandler()
        ],
        level=logging.DEBUG
        )

    bot = Bot(settings.TOKEN)

    app = web.Application()

    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dispatcher,
        bot=bot,
        secret_token=WEBHOOK_SECRET,
    )

    webhook_requests_handler.register(app, path=WEBHOOK_PATH)

    # Mount dispatcher startup and shutdown hooks to aiohttp application
    setup_application(app, dispatcher, bot=bot)

    # And finally start webserver
    web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)


if __name__ == '__main__':
    main()
    # asyncio.run(main())


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
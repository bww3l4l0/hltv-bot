import os
import asyncio
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from core.menu import top_level_router
from core.predictions import prediction_router


load_dotenv()

TOKEN = os.getenv('TOKEN')

dispatcher = Dispatcher()

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
# Работать через евент луп и экзекьютор
# Семафор зависит от количества прокси
# Функции предикт и предикт лайв день завтра
# Кэш(мб через редис) или aiocache


#  to do
# обучить хоть какую-то модель
# написать парсер ссылок для матчей
# CallbackAnswerMiddleware

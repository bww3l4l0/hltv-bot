import os
import asyncio
import logging
from core.menu import top_level_router
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher

load_dotenv()

TOKEN = os.getenv('TOKEN')
dispatcher = Dispatcher()
logger = logging.getLogger(__name__)
logging.basicConfig(filename='hltv_v2_log.log', filemode='w')

routers = [top_level_router]

dispatcher.include_routers(*routers)


async def main() -> None:
    bot = Bot(TOKEN)
    await dispatcher.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())

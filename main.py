import os
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.types.message import Message
from aiogram.filters import Command, CommandStart

load_dotenv()

TOKEN = os.getenv('TOKEN')
dispatcher = Dispatcher()


@dispatcher.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer('привет')


async def main() -> None:
    bot = Bot(TOKEN)
    await dispatcher.start_polling(bot)


if __name__ == '__main__':
    print(TOKEN)
    asyncio.run(main())

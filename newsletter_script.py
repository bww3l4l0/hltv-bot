import os
import asyncio
import pickle
import logging
from concurrent.futures import ProcessPoolExecutor
from argparse import ArgumentParser, Namespace
from dotenv import load_dotenv
from aiogram import Bot
from textwrap import dedent
from parser.hltv_parser_extended_data import process_match
from parser.match_url_parser import fetch_match_urls
from parser.prepocessing import preprocess
from core.predictions import make_result_str


load_dotenv()

TOKEN = os.getenv('TOKEN')

CHAT_ID = 993955495

pool = ProcessPoolExecutor(2)

with open('core/model/hltv_v2_model_dump', 'rb') as file:
    model = pickle.load(file)

logger = logging.getLogger(__name__)
logging.basicConfig(filemode='r', filename='hltv2_script.log')


def read_cl_arguments() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument('--date', type=str)
    return parser.parse_args()


async def process_match_wrapper(url: str, bot: Bot) -> None:

    event_loop = asyncio.get_running_loop()
    try:
        data = await event_loop.run_in_executor(pool, process_match, url)

    except Exception as e:
        await bot.send_message(chat_id=CHAT_ID,
                               text=dedent(f'''url: {url}\nневозможно извлечь нужные данные'''))
        logger.exception(e)
        return

    if type(data) is dict:
        try:
            data = preprocess(data)
            prediction = model.predict_proba(data)
            message_text = make_result_str(data, prediction)
            await bot.send_message(chat_id=CHAT_ID,
                                   text=message_text)
            return
        except Exception as e:
            await bot.send_message(chat_id=CHAT_ID,
                                   text=dedent(f'''url; {url}\nневозможно сделать предсказание'''))
            logger.exception(e)


async def main() -> None:
    bot = Bot(TOKEN)

    args = read_cl_arguments()
    data = args.date
    match_urls = fetch_match_urls(data)

    tasks = [process_match_wrapper(url, bot) for url in match_urls]

    await asyncio.gather(*tasks)

    await bot.close()


if __name__ == '__main__':
    asyncio.run(main())

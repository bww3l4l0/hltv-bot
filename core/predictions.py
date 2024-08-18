import re
import asyncio
import pickle
from aiogram import Router
from aiogram.types.message import Message
from core.state_machines import RoutingFsm
from aiogram.fsm.context import FSMContext
from concurrent.futures import ThreadPoolExecutor
from parser.hltv_parser_extended_data import process_match
from parser.prepocessing import preprocess

pool = ThreadPoolExecutor(4)

prediction_router = Router(name='predictions')

regex_pattern = re.compile(
    r"^(?:http|ftp)s?://"
    r"(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?$)"
    r"(?::\d+)?"
    r"(?:/?|[/?]\S+)$", re.IGNORECASE)

with open('/home/sasha/Documents/vscode/hltv v2 bot/core/model/hltv_v2_model_dump', 'rb') as file:
    model = pickle.load(file)

semaphore = asyncio.Semaphore(2)


def validated_url(url: str) -> bool:
    return re.match(regex_pattern, url) is not None


@prediction_router.message(RoutingFsm.getting_url)
async def get_url(message: Message, state: FSMContext) -> None:

    url = message.text

    if validated_url(message.text):
        await message.answer('url is validated')

    event_loop = asyncio.get_running_loop()

    async with semaphore:
        data = await event_loop.run_in_executor(pool, process_match, url)

    data = preprocess(data)

    predict = model.predict_proba(data)

    await message.answer(str(predict))

    await state.set_state(RoutingFsm.none)

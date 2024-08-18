import asyncio
import urllib3
import re
from concurrent.futures import ThreadPoolExecutor
from model.test_model_load import model
from prepocessing import preprocess


import urllib3.util
# from parser import process_match
from hltv_parser_extended_data import process_match

# 1й вариант правильный
async def main() -> None:
    url = 'https://www.hltv.org/matches/2374326/vitality-vs-natus-vincere-iem-cologne-2024'

    pool = ThreadPoolExecutor()
    event_loop = asyncio.get_event_loop()

    pool.submit

    res = await event_loop.run_in_executor(pool, process_match, url)
    # res.add_done_callback
    print(res)

# 2й вариант тоже правильный но без евент лупа и с executor
async def main() -> None:
    url = 'https://www.hltv.org/matches/2374326/vitality-vs-natus-vincere-iem-cologne-2024'

    pool = ThreadPoolExecutor()
    # event_loop = asyncio.get_event_loop()

    res = pool.submit(process_match, url)
    res = await asyncio.wrap_future(res)
    # res = await event_loop.run_in_executor(pool, process_match, url)

    # res.add_done_callback
    print(res)

# 3й вариант тоже правильный но без евент лупа и пула но с методом to_thread
# самый простой метод и не красивый
async def main() -> None:
    url = 'https://www.hltv.org/matches/2374326/vitality-vs-natus-vincere-iem-cologne-2024'

    # pool = ThreadPoolExecutor()
    # event_loop = asyncio.get_event_loop()
    res = await asyncio.to_thread(process_match, url)

    res = preprocess(res)

    res = model.predict_proba(res)



    # res = pool.submit(process_match, url)
    # res = await asyncio.wrap_future(res)
    # res = await event_loop.run_in_executor(pool, process_match, url)

    # res.add_done_callback
    print(res)


def verify_url() -> bool:
    # asyncio.run(main())
    url = 'https://www.hltv.org/matches/2374326/vitality-vs-natus-vincere-iem-cologne-2024'
    parsed = urllib3.util.parse_url(url)
    print(parsed.scheme == 'https')
    print(parsed.host == 'www.hltv.org')

    pattern = re.compile('/matches/d{7}/')
    print(re.match(pattern, parsed.path))

    print(parsed.path)


if __name__ == '__main__':
    asyncio.run(main())

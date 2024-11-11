from aiogram import Router
from aiogram.types.message import Message
from aiogram.filters import Command
from redis.asyncio import Redis

newsleter_router = Router()
USERS_REDIS_KEY = 'bot_subscribers'


@newsleter_router.message(Command('enable'))
async def enable(message: Message, redis: Redis) -> None:
    '''
    /enable handler(подключение рассылки)
    '''
    if await redis.sismember(USERS_REDIS_KEY, message.from_user.id):
        await message.answer('вы уже подписаны')
        return
    await redis.sadd(USERS_REDIS_KEY, message.from_user.id)
    await message.answer('вы подписались на рассылку')


@newsleter_router.message(Command('disable'))
async def disable(message: Message, redis: Redis) -> None:
    '''
    /disable handler(отключение рассылки)
    '''
    if not await redis.sismember(USERS_REDIS_KEY, message.from_user.id):
        await message.answer('вы не подписаны')
        return
    await redis.srem(USERS_REDIS_KEY, message.from_user.id)
    await message.answer('вы отписались от рассылки')

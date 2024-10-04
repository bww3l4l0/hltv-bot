from aiogram.filters import Filter
from aiogram.types.message import Message
from settings import settings
# ADMIN_ID = 993955495


class IsAdmin(Filter):
    def __init__(self) -> None:
        super().__init__()

    async def __call__(self, message: Message) -> bool:
        return message.from_user.id == settings.ADMIN_ID

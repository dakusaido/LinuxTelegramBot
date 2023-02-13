from aiogram import types
from aiogram.dispatcher.filters import BoundFilter


class PrivateChatFilter(BoundFilter):
    async def check(self, message: types.Message):
        return message.text

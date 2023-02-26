import re
import typing

from aiogram import types
from aiogram.dispatcher.filters import BoundFilter


class PrivateChatFilter(BoundFilter):
    async def check(self, message: types.Message):
        return message.text


class DeleteOneKey(BoundFilter):

    def __init__(self, pattern: re.Pattern):

        if not isinstance(pattern, re.Pattern):
            raise TypeError('pattern should be re.Pattern')

        self.delete_one_key_pattern = pattern

    async def check(self, callback_query: types.CallbackQuery) -> bool:
        return bool(self.delete_one_key_pattern.findall(callback_query.data))


class ShowLocationButtons(BoundFilter):
    pass


class CallbackQueryFilter(BoundFilter):

    def __init__(self, callback_query_data: typing.Union[typing.Iterable, str]):
        if isinstance(callback_query_data, str):
            self.callback_query_data = [callback_query_data]

        self.callback_query_data = callback_query_data

    async def check(self, callback_query: types.CallbackQuery) -> bool:
        return callback_query.data in self.callback_query_data

import re

from aiogram import types
from aiogram.dispatcher.filters import BoundFilter


class PrivateChatFilter(BoundFilter):
    async def check(self, message: types.Message):
        return message.text


class DeleteOneKey(BoundFilter):
    delete_one_keys_pattern = re.compile(r'(delete_one [1-5])')

    async def check(self, message: types.Message) -> bool:
        return bool(self.delete_one_keys_pattern.findall(message.text))


if __name__ == '__main__':
    delete_one_keys_pattern = re.compile(r'(delete_one [1-5])')
    text = 'delete_one 2'
    print(bool(delete_one_keys_pattern.findall(text)))
import asyncio
from abc import ABC

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

from typing import *

default_sleep = 0.005


class Markup(ABC):

    def __init__(self):
        pass

    def __str__(self):
        pass

    async def get_inline_keyboard(
            self,
            iterable: Union[Iterable[InlineKeyboardButton], Dict, str],
            **kwargs
    ) -> InlineKeyboardMarkup:

        if isinstance(iterable, Dict):
            return await self._get_inline_keyboard_dict(iterable, **kwargs)

        if isinstance(iterable, str):
            iterable = [InlineKeyboardButton(iterable)]

        return await self._get_inline_keyboard(*iterable, **kwargs)

    async def get_reply_keyboard(
            self,
            iterable: Union[Iterable[KeyboardButton], str],
            **kwargs
    ) -> ReplyKeyboardMarkup:

        if isinstance(iterable, str):
            iterable = [KeyboardButton(iterable)]

        return await self._get_reply_keyboard(iterable, **kwargs)

    async def _get_inline_keyboard_dict(self, data: Dict, **kwargs) -> InlineKeyboardMarkup:

        pattern = kwargs.get('pattern') or "#{0} {1}"

        buttons = map(
            lambda key: InlineKeyboardButton(
                pattern.format(key, data.get(key)),
                callback_data=key
            ),
            data.keys()
        )

        keyboard = await self._get_inline_keyboard(buttons, **kwargs)

        return keyboard

    @staticmethod
    async def _get_inline_keyboard(iterable: Iterable[InlineKeyboardButton], **kwargs) -> InlineKeyboardMarkup:
        await asyncio.sleep(default_sleep)

        resize_keyboard = kwargs.get('resize_keyboard')

        keyboard = InlineKeyboardMarkup(
            resize_keyboard=resize_keyboard or True
        )

        for button in iterable:
            keyboard.add(button)

        return keyboard

    @staticmethod
    async def _get_reply_keyboard(iterable: Iterable[KeyboardButton], **kwargs) -> ReplyKeyboardMarkup:
        await asyncio.sleep(default_sleep)

        resize_keyboard = kwargs.get('resize_keyboard')

        keyboard = ReplyKeyboardMarkup(
            resize_keyboard=resize_keyboard or True
        )

        for button in iterable:
            if isinstance(button, List):
                keyboard.add(*button)
                continue

            keyboard.add(button)

        return keyboard

import asyncio

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from factorys import Markup

from typing import *

default_sleep = 0.005


class Markups(Markup):

    async def main_menu(self, language: Dict[str, str]) -> ReplyKeyboardMarkup:
        what_is_it: str = language.get('what_is_it')
        how_to_use_bot: str = language.get('how_to_use_bot')
        commands: str = language.get('commands')

        buttons = [
            [KeyboardButton(what_is_it), KeyboardButton(how_to_use_bot)],
            KeyboardButton(commands)
        ]

        keyboard = await self.get_reply_keyboard(buttons)

        return keyboard

    async def location_menu(self, language: Dict[str, str]) -> ReplyKeyboardMarkup:
        use_geolocation = language.get('use_geolocation')
        add_new = language.get('add_new')
        cancel = language.get('cancel')

        buttons = [
            [KeyboardButton(use_geolocation), KeyboardButton(add_new)],
            KeyboardButton(cancel)
        ]

        keyboard = await self.get_reply_keyboard(buttons)

        return keyboard

    @staticmethod
    async def commands(language: Dict[str, str], show: bool = True, reset: bool = True) -> InlineKeyboardMarkup:
        await asyncio.sleep(default_sleep)

        add_new_location = language.get('add_new_location')
        show_saved_locations = language.get('show_saved_locations')
        remove_all_saved_locations = language.get('remove_all_saved_locations')

        keyboard = InlineKeyboardMarkup()
        add_location = InlineKeyboardButton(add_new_location, callback_data='add_location')
        show_locations = InlineKeyboardButton(show_saved_locations, callback_data='show_locations')
        reset_list = InlineKeyboardButton(remove_all_saved_locations, callback_data='reset_list')

        keyboard.add(add_location)

        if show:
            keyboard.add(show_locations)

        if reset:
            keyboard.add(reset_list)

        return keyboard

    @staticmethod
    async def show_location(language: Dict[str, str]) -> InlineKeyboardMarkup:
        await asyncio.sleep(default_sleep)

        back_text = language.get('back')
        next_text = language.get('next')
        choose_text = language.get('choose')

        keyboard = InlineKeyboardMarkup()
        back = InlineKeyboardButton(back_text, callback_data='back')
        next_ = InlineKeyboardButton(next_text, callback_data='next')
        choose = InlineKeyboardButton(choose_text, callback_data='choose')

        keyboard.add(back, next_)
        keyboard.add(choose)

        return keyboard

    async def show_locations_list_keyboard(self, data: Dict) -> InlineKeyboardMarkup:
        dict_ = {key: value.get('name') for key, value in data.items()}

        keyboard = await self.get_inline_keyboard(dict_)

        return keyboard

    async def get_reply_keyboard_use_str(self, *args) -> ReplyKeyboardMarkup:
        buttons = map(KeyboardButton, args)
        keyboard = await self.get_reply_keyboard(buttons)

        return keyboard

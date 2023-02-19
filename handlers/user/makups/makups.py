from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from language_packages import LanguagePackage

from typing import Dict


class Markups:

    @staticmethod
    def mainMenu(language: Dict[str, str]) -> ReplyKeyboardMarkup:
        what_is_it: str = language.get('what_is_it')
        how_to_use_bot: str = language.get('how_to_use_bot')
        commands: str = language.get('commands')

        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

        keyboard.add(KeyboardButton(what_is_it), KeyboardButton(how_to_use_bot))
        keyboard.add(KeyboardButton(commands))

        return keyboard

    @staticmethod
    def locationMenu(language: Dict[str, str]) -> ReplyKeyboardMarkup:
        use_geolocation = language.get('use_geolocation')
        add_new = language.get('add_new')
        cancel = language.get('cancel')

        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(KeyboardButton(use_geolocation), KeyboardButton(add_new))
        keyboard.add(KeyboardButton(cancel))

        return keyboard

    @staticmethod
    def commands(language: Dict[str, str]) -> InlineKeyboardMarkup:
        add_new_location = language.get('add_new_location')
        show_saved_locations = language.get('show_saved_locations')
        remove_all_saved_locations = language.get('remove_all_saved_locations')

        keyboard = InlineKeyboardMarkup()
        add_location = InlineKeyboardButton(add_new_location, callback_data='add_location')
        show_locations = InlineKeyboardButton(show_saved_locations, callback_data='show_locations')
        reset_list = InlineKeyboardButton(remove_all_saved_locations, callback_data='reset_list')

        keyboard.add(add_location)
        keyboard.add(show_locations)
        keyboard.add(reset_list)

        return keyboard

    @staticmethod
    def showLocation(language: Dict[str, str]) -> InlineKeyboardMarkup:
        back_text = language.get('back')
        next_text = language.get('next')
        show_all_text = language.get('show_all')
        choose_text = language.get('choose')

        keyboard = InlineKeyboardMarkup()
        back = InlineKeyboardButton(back_text, callback_data='back')
        next_ = InlineKeyboardButton(next_text, callback_data='next')
        show_all = InlineKeyboardButton(show_all_text, callback_data='show_all')
        choose = InlineKeyboardButton(choose_text, callback_data='choose')

        keyboard.add(back, next_)
        keyboard.add(show_all)
        keyboard.add(choose)

        return keyboard

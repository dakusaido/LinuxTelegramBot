import asyncio
import utils

from aiogram import types
from aiogram.dispatcher import FSMContext

from typing import (Dict, )
from functools import wraps

__all__ = ['LanguagePackage']


class LanguagePackage:
    default_language = 'ru'
    language_package_file = 'patterns/handlers_user_functions.json'
    default_path_to_lang_pac = utils.get_project_path() + language_package_file

    def __init__(self, languages: Dict[str, Dict] = None, path_to_language_pac: str = None):
        self.path_to_language_pac = path_to_language_pac or self.default_path_to_lang_pac

        dict_from_json = utils.get_dict_from_json(self.path_to_language_pac)
        self.languages = languages or dict_from_json

    def get_language_package(self, language: str = None):
        cur_language = self.languages.get(language or self.default_language)

        return cur_language

    def ru(self):
        return self.get_language_package('ru')

    def en(self):
        return self.get_language_package('en')

    def decorator(self, func):
        @wraps(func)
        async def wrapper(message: types.Message | types.CallbackQuery, state: FSMContext, *args, **kwargs):
            locate = message.from_user.language_code
            language = self.get_language_package(locate)

            result = await func(message, state, *args, **kwargs, language=language)

            return result

        return wrapper

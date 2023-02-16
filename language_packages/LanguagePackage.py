import json
import utils

from aiogram import types
from typing import (Dict, )

__all__ = ['LanguagePackage']

default_path_to_lang_pac = utils.get_project_path() + 'patterns/handlers_user_functions.json'
default_language = 'ru'


class LanguagePackage:
    language = None

    def __init__(self, language: str = None, languages: Dict[str, Dict] = None, path_to_language_pac: str = None):

        self.path_to_language_pac = path_to_language_pac or default_path_to_lang_pac
        self.languages = languages or utils.get_dict_from_json(self.path_to_language_pac)
        self.language = language or default_language

    def get_language_package(self, message_from_user: types.Message | types.CallbackQuery) -> dict:

        user_region = self.language or message_from_user.from_user.language_code

        return self.languages.get(user_region, default_language)

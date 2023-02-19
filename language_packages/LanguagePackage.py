import json
import utils

from aiogram import types
from typing import (Dict, )

__all__ = ['LanguagePackage']

default_path_to_lang_pac = utils.get_project_path() + 'patterns/handlers_user_functions.json'
default_language = 'ru'


class LanguagePackage:

    def __init__(self, languages: Dict[str, Dict] = None, path_to_language_pac: str = None):
        self.path_to_language_pac = path_to_language_pac or default_path_to_lang_pac
        self.languages = languages or utils.get_dict_from_json(self.path_to_language_pac)

    def get_language_package(self, language: str = None) -> Dict[str, str]:
        return self.languages.get(language or default_language, default_language)

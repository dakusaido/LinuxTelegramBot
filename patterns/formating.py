import asyncio

from language_packages import LanguagePackage

__all__ = ['format_pattern']

language = LanguagePackage()


class Default(dict):

    def __missing__(self, key):
        language_package = language.get_language_package()
        default = language_package.get('missed')

        return default


async def format_pattern(pattern: str, **kwargs):
    await asyncio.sleep(1)
    return pattern.format_map(Default(**kwargs))

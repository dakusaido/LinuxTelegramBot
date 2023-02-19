from language_packages import LanguagePackage

__all__ = ['format_pattern']

language = LanguagePackage()


class Default(dict):

    def __missing__(self, key):
        default = language.get_language_package().get('missed')

        return default


def format_pattern(pattern: str, **kwargs):
    return pattern.format_map(Default(**kwargs))

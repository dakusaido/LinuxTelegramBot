from requests import get
from json import dump
from fake_useragent import UserAgent
from data import API_KEY
from typing import List, Dict, Any

__all__ = ['get_place']


def get_place(name: str, latitude: float, longitude: float, radius: int, api_key: str = API_KEY) -> List[Dict]:

    attr_is_not_valid = lambda attr: TypeError(f"attr {attr} is not valid")

    if not isinstance(name, str):
        raise attr_is_not_valid(name)

    if not isinstance(latitude, float):
        raise attr_is_not_valid(latitude)

    if not isinstance(longitude, float):
        raise attr_is_not_valid(longitude)

    if not isinstance(api_key, str):
        raise attr_is_not_valid(api_key)

    if len(name) > 15:
        raise Exception('Invalid name')

    return _get_place(name, latitude, longitude, radius, api_key)


def _get_place(name: str, latitude: float, longitude: float, radius: int, api_key: str = API_KEY) -> List[Dict]:
    ...


if __name__ == '__main__':
    print(get_place('asd asd', 2, 2, 2))

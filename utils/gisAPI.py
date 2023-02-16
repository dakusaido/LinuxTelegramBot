import aiogram.utils.markdown as markdown

from requests import get
from json import dump
from fake_useragent import UserAgent
from typing import List, Dict, Any
from patterns import show_saved_locations_text

__all__ = ['get_place', 'format_place', 'get_components']


def get_place(name: str, latitude: float, longitude: float, radius: int, api_key: str) -> List[Dict]:
    attr_is_not_valid = lambda attr: TypeError(f"attr {attr} is not valid")

    if not isinstance(name, str):
        raise attr_is_not_valid(name)

    if not isinstance(latitude, float):
        raise attr_is_not_valid(latitude)

    if not isinstance(longitude, float):
        raise attr_is_not_valid(longitude)

    if not isinstance(api_key, str):
        raise attr_is_not_valid(api_key)

    if len(name) > 40:
        raise Exception('Invalid name')

    return _get_place(name, latitude, longitude, radius, api_key)


def _get_place(name: str, latitude: float, longitude: float, radius: int, api_key: str) -> bool | List:
    source = 'https://catalog.api.2gis.com/3.0/items'

    params = {
        'q': name,
        'location': f'{longitude},{latitude}',
        'radius': radius,
        'key': api_key
    }

    response = get(source, params=params).json()

    code = response.get('meta').get('code')

    if code != 200:
        return False

    result = response.get('result')

    if not result:
        return False

    items = result.get('items')

    if not items:
        return False

    return items


def get_components(place: Dict[str, str | Dict]):
    default = 'Отсутствует'

    address_comment = place.get('address_comment')  # 2
    address_name = place.get('address_name')  # 1

    ads = place.get('ads')
    id_ = place.get('id') or default
    name = place.get('name') or default  # 0
    type_ = place.get('type') or default

    link = default
    article = default
    text = default
    href_link = default
    location = default

    if address_name:
        location = address_name

        if address_comment:
            location += ', ' + address_comment

    if ads is dict:
        article = ads.get('article') or ads.get('article_warning') or default  # 4
        link = ads.get('link') or default
        text = ads.get('text') or ads.get('text_warning') or default  # 5

        if link != default:
            link_text = link.get('text', 'Ссылка')
            link_value = link.get('value') or default
            href_link = markdown.link(link_text, link_value) if link_value != default else default

    return dict(name=name, location=location, link=href_link, info=article, more_info=text)


def format_place(place: Dict[str, str | Dict]):
    TEXT = show_saved_locations_text
    components = get_components(place)

    return TEXT.format(*components.values())


if __name__ == '__main__':
    example = {'address_name': 'улица Пушкина, 86', 'building_name': 'Национальная библиотека Республики Татарстан',
               'full_name': 'Казань, Национальная библиотека Республики Татарстан', 'id': '70000001045588702',
               'name': 'Национальная библиотека Республики Татарстан', 'purpose_name': 'Культурное учреждение',
               'type': 'branch'}

    print(format_place(example))
    print(get_components(example))

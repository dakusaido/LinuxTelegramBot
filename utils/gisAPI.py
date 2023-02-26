import asyncio

import aiogram.utils.markdown as markdown

from typing import List, Dict, Any, Iterable

import aiohttp

from language_packages import LanguagePackage

from geopy.distance import distance

from patterns import format_pattern

__all__ = ['get_place', 'format_place', 'get_components', 'get_distance', 'get_many_components',
           'get_names_and_distances', 'sort_names_and_distance', 'get_five_elements', 'add_distance',
           'get_cur_component', 'get_component_materials']

language_package = LanguagePackage()
sleep_time = 0.5


async def get_place(name: str, latitude: float, longitude: float, radius: int, api_key: str):
    if not isinstance(name, str):
        raise TypeError(f"attr {name} is not valid")

    if not isinstance(latitude, float):
        raise TypeError(f"attr {latitude} is not valid")

    if not isinstance(longitude, float):
        raise TypeError(f"attr {longitude} is not valid")

    if not isinstance(api_key, str):
        raise TypeError(f"attr {api_key} is not valid")

    if len(name) > 40:
        raise Exception('Invalid name')

    return await _get_place(name, latitude, longitude, radius, api_key)


async def _get_place(name: str, latitude: float, longitude: float, radius: int, api_key: str):
    source = 'https://catalog.api.2gis.com/3.0/items'

    params = {
        'q': name,
        'location': f'{longitude},{latitude}',
        'radius': radius,
        'key': api_key,
        'fields': 'items.point'
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(source, params=params) as resp:
            response = await resp.json()

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


async def get_components(place: Dict[str, Any]):
    await asyncio.sleep(sleep_time)

    default = 'Отсутствует'

    address_comment = place.get('address_comment')  # 2
    address_name = place.get('address_name')  # 1

    ads = place.get('ads')
    # id_ = place.get('id') or default
    name = place.get('name') or default  # 0
    point = place.get('point')
    # type_ = place.get('type') or default

    # link = default
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

    return dict(name=name, location=location, point=point, link=href_link, info=article, more_info=text)


async def get_many_components(places: List[Dict[str, Any]]):
    result = []

    for place in places:
        component = await get_components(place)
        result.append(component)

    return result


async def get_names_and_distances(components: List[Dict[str, Any]], position: Iterable[float]):
    result = []

    await asyncio.sleep(sleep_time)

    for component in components:
        point = component.get('point')
        result.append(
            dict(
                name=component.get('name'),
                distance=get_distance(
                    position_1=position,
                    position_2=(point.get('lon'), point.get('lat'))
                ).m.__round__()
            )
        )

    return result


async def add_distance(components: List[Dict[str, Any]], position: Iterable[float]):
    for component in components:
        point = component.get('point')
        lat = point.get('lat')
        lon = point.get('lon')
        distance_ = get_distance(position, (lon, lat)).m.__round__()

        component.__setitem__('distance', distance_)

    return components


def sort_names_and_distance(names: List[Dict[str, Any]]):
    return sorted(names, key=lambda dict_: dict_.get('distance'))


def get_five_elements(names: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sort_names_and_distance(names)[:5]


async def format_place(place: Dict[str, str | Dict], lang: str):
    language = await language_package.get_language_package(lang)
    text = language.get('show_saved_locations_text')
    components = await get_components(place)

    return format_pattern(text, **components)


def get_distance(position_1: Iterable[float], position_2: Iterable[float]):
    return distance(position_1, position_2)


def get_cur_component(components: List[Dict[str, Any]], index: int) -> Dict[str, Any]:
    return components[index]


async def get_component_materials(component: Dict[str, Any], pattern_text: str):
    text = await format_pattern(pattern_text, **component)

    point = component.get('point')
    component_lat = point.get('lat')
    component_lon = point.get('lon')

    return text, component_lat, component_lon


if __name__ == '__main__':
    example = [
        {'name': 'Пятёрочка, супермаркет', 'location': 'Журналистов, 7', 'point': {'lat': 55.807776, 'lon': 49.189992},
         'link': 'Отсутствует', 'info': 'Отсутствует', 'more_info': 'Отсутствует'},
        {'name': 'Пятёрочка, супермаркет', 'location': 'Сибирский тракт, 17, 1 этаж',
         'point': {'lat': 55.808446, 'lon': 49.181708}, 'link': 'Отсутствует', 'info': 'Отсутствует',
         'more_info': 'Отсутствует'}, {'name': 'Пятёрочка, супермаркет', 'location': 'Сибирский тракт, 10а, 1 этаж',
                                       'point': {'lat': 55.80652, 'lon': 49.184395}, 'link': 'Отсутствует',
                                       'info': 'Отсутствует', 'more_info': 'Отсутствует'},
        {'name': 'Пятёрочка, супермаркет', 'location': 'Академика Губкина улица, 44',
         'point': {'lat': 55.807095, 'lon': 49.1946}, 'link': 'Отсутствует', 'info': 'Отсутствует',
         'more_info': 'Отсутствует'},
        {'name': 'Пятёрочка, супермаркет', 'location': 'Академика Губкина улица, 75, 1 этаж',
         'point': {'lat': 55.811456, 'lon': 49.204202}, 'link': 'Отсутствует', 'info': 'Отсутствует',
         'more_info': 'Отсутствует'},
        {'name': 'Пятёрочка, супермаркет', 'location': 'Галеева, 8а к1', 'point': {'lat': 55.803217, 'lon': 49.176348},
         'link': 'Отсутствует', 'info': 'Отсутствует', 'more_info': 'Отсутствует'},
        {'name': 'Пятёрочка, супермаркет', 'location': 'Академика Губкина улица, 116, 1 этаж',
         'point': {'lat': 55.810908, 'lon': 49.204535}, 'link': 'Отсутствует', 'info': 'Отсутствует',
         'more_info': 'Отсутствует'}, {'name': 'Пятёрочка, супермаркет', 'location': 'Космонавтов, 30, 1 этаж',
                                       'point': {'lat': 55.797002, 'lon': 49.189991}, 'link': 'Отсутствует',
                                       'info': 'Отсутствует', 'more_info': 'Отсутствует'},
        {'name': 'Пятёрочка, супермаркет', 'location': 'Зур Урам, 1к', 'point': {'lat': 55.801903, 'lon': 49.202695},
         'link': 'Отсутствует', 'info': 'Отсутствует', 'more_info': 'Отсутствует'},
        {'name': 'Пятёрочка, супермаркет', 'location': 'Николая Ершова, 62в к2',
         'point': {'lat': 55.796936, 'lon': 49.17985}, 'link': 'Отсутствует', 'info': 'Отсутствует',
         'more_info': 'Отсутствует'}]

    print(add_distance(example, (34, 12)))

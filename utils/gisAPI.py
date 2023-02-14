import aiogram.utils.markdown as markdown

from requests import get
from json import dump
from fake_useragent import UserAgent
from typing import List, Dict, Any
from patterns import show_saved_locations_text


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

    if len(name) > 15:
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
    example = {"address_comment": "цокольный этаж", "address_name": "проспект Ямашева, 51Б", "ads": {
        "article": "Почему мы:<br /><br />•&nbsp;большой опыт — работаем с 2006 года;<br />•&nbsp;обеды от 100 руб., большой выбор блюд;<br />•&nbsp;вечерний комплекс на ужин за 500 руб., в который входит салат, второе, гарнир и напиток;<br />•&nbsp;уютная обстановка.<br />Кафе «Мастер вкуса» — это уютное место для проведения свадебных торжеств, товарищеских встреч, юбилейных банкетов, семейных и детских праздников. <br /><br />Войдя в наше кафе, вы поймете, что это то самое место для проведения вашего праздника, которое оставит у вас приятное впечатление, сэкономит ваши деньги и порадует вкусной домашней едой. <br /><br />Также есть приятный бонус для посетителей — напитки с собой*.<br /><br />*Подробности узнавайте у персонала заведения либо по телефону.",
        "link": {"text": "Выбрать вид меню",
                 "value": "http://link.2gis.com/1.2/B11FC7E4/webapi/20230201/project21/2956015536474329/null/vf6fEg6917G2J3A86143GGGGl1yj5446G6G40978789535AHuDfz9A298J6AG4I1G46J4JGJku6luv6A66292565961H2J47HH17f?http://cafemastervkusa.ru/menyu"},
        "text": "Получи десерт в подарок при заказе от 350р."}, "id": "2956015536474329",
               "name": "Мастер вкуса, кафе домашней еды", "type": "branch"}

    print(format_place(example))
    print(get_components(example))

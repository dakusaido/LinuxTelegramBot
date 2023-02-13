import json
import os

from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, desc

import utils
from utils.datbase import session
from utils.schemas import User, UserLocations

from typing import Dict, List


def register_user(tg_id: int, first_name: str, second_name: str):
    session.connection()
    user = User(
        tg_id=tg_id,
        first_name=first_name,
        second_name=second_name
    )
    session.add(user)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()


def delete_user(tg_id):
    user = session.query(User).filter(User.tg_id.like(tg_id)).one()
    session.delete(user)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()


def select_users():
    users = session.query(User).all()
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
    return users


def get_user(tg_id):
    user = session.query(User).filter(User.tg_id.like(tg_id)).one()

    try:
        session.commit()
    except IntegrityError:
        session.rollback()

    return user.second_name, user.first_name


def register_new_data(tg_id: int, data: Dict):
    session.connection()
    user_location_data = UserLocations(
        tg_id=tg_id,
        data=json.dumps(data)
    )

    session.add(user_location_data)

    try:
        session.commit()
    except Exception as e:
        print(e)
        session.rollback()
        return False

    return user_location_data


def add_data(tg_id: int, latitude: float, longitude: float, name=None, img=None, info=None):
    if not isinstance(latitude, float):
        return False

    if not isinstance(longitude, float):
        return False

    if not isinstance(name, str):
        return False

    new_dict = dict(tg_id=tg_id, latitude=latitude, longitude=longitude)

    for attr, value in zip(('name', 'img', 'info'), (name, img, info)):
        new_dict[attr] = value

    return _add_data(tg_id, new_dict)


def _add_data(tg_id: int, data: Dict):
    try:
        user_location_data = session.query(UserLocations).filter(UserLocations.tg_id.like(tg_id)).one()

    except Exception as e:
        print(e)
        return register_new_data(tg_id, {1: data})

    user_dict = json.loads(user_location_data.data)

    user_dict_len = user_dict.__len__() + 1

    user_dict.__setitem__(user_dict_len, data)

    user_location_data.data = json.dumps(user_dict)
    session.add(user_location_data)
    session.commit()

    return user_location_data


def show_locations(tg_id):
    try:
        user_location_data = session.query(UserLocations).filter(UserLocations.tg_id.like(tg_id)).one()

    except Exception as e:
        print(e)
        return {}

    finally:
        session.commit()

    return json.loads(user_location_data.data)


def location_list_len(tg_id):
    data = show_locations(tg_id)

    return data.__len__()


def delete_data(tg_id):
    try:
        user_location = session.query(UserLocations).filter(UserLocations.tg_id.like(tg_id)).one()

    except Exception as e:
        print(e)
        return False

    if user_location == '{}':
        return True

    user_location_data = json.loads(user_location.data)
    path = utils.get_project_path() + f'data/imgs/{tg_id}_'

    for key, value in user_location_data.items():
        if value.get('img'):
            if os.path.exists(path + key + '.png'):
                os.remove(path + key + '.png')

    try:
        user_location.data = '{}'
        session.commit()

    except Exception as e:
        print(e)
        return False

    except IntegrityError:
        session.rollback()

    return True


def delete_one(tg_id: int, data: Dict, key: str):
    removed_data: dict = data.pop(key)

    new_data = {}
    path = utils.get_project_path() + f'data/imgs/{tg_id}_'

    for i, key in enumerate(data.keys(), start=1):
        new_data[str(i)] = data.get(key)

        if data.get(key).get('img'):
            if os.path.exists(path + key + '.png'):
                os.rename(path + key + '.png', path + str(i) + '.png')

    try:
        user_location = session.query(UserLocations).filter(UserLocations.tg_id.like(tg_id)).one()

    except Exception as e:
        print(e)
        return False

    try:
        user_location.data = json.dumps(new_data)
        session.commit()

    except Exception as e:
        print(e)
        return False

    except IntegrityError:
        session.rollback()

    path = utils.get_project_path() + f'data/imgs/{tg_id}_'

    if removed_data.get('img'):
        if os.path.exists(path + key + '.png'):
            os.remove(path + key + '.png')

    return True

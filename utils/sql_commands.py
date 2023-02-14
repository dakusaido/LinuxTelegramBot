import json
import os

from sqlalchemy.exc import IntegrityError

import utils
from utils.datbase import session
from utils.schemas import User, UserLocations

from typing import Dict, List
from functools import wraps

__all__ = ['register_user', 'select_users', 'delete_user', 'get_user', 'show_locations', 'add_data',
           'location_list_len', 'delete_data', 'delete_one']


def session_action(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        session.connection()
        try:
            result = func(*args, **kwargs)
            session.commit()

        except IntegrityError:
            session.rollback()
            return False

        except Exception as e:
            print(e)
            return False

        return result

    return wrapper


@session_action
def register_user(tg_id: int, first_name: str, second_name: str):
    user = User(
        tg_id=tg_id,
        first_name=first_name,
        second_name=second_name
    )
    session.add(user)


@session_action
def delete_user(tg_id):
    user = session.query(User).filter(User.tg_id.like(tg_id)).one()
    session.delete(user)


def select_users():
    users = session.query(User).all()
    return users


@session_action
def get_user(tg_id):
    user = session.query(User).filter(User.tg_id.like(tg_id)).one()

    return user


@session_action
def register_new_data(tg_id: int, data: Dict):
    user_location_data = UserLocations(
        tg_id=tg_id,
        data=json.dumps(data)
    )

    session.add(user_location_data)

    return user_location_data


@session_action
def add_data(tg_id: int, latitude: float, longitude: float, **kwargs):
    if not isinstance(latitude, float):
        return False

    if not isinstance(longitude, float):
        return False

    for key in kwargs.keys():
        if not isinstance(key, str):
            return False

    new_dict = dict(tg_id=tg_id, location=(longitude, latitude))
    new_dict.update(kwargs)

    return _add_data(tg_id, new_dict)


@session_action
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


@session_action
def show_locations(tg_id):
    try:
        user_location_data = session.query(UserLocations).filter(UserLocations.tg_id.like(tg_id)).one()

    except Exception as e:
        print(e)
        return {}

    return json.loads(user_location_data.data)


def location_list_len(tg_id):
    data = show_locations(tg_id)

    return data.__len__()


@session_action
def delete_data(tg_id):
    try:
        user_location = session.query(UserLocations).filter(UserLocations.tg_id.like(tg_id)).one()

    except Exception as e:
        print(e)
        return False

    user_location_data = json.loads(user_location.data)

    if not user_location_data:
        return True

    path = utils.get_project_path() + f'data/imgs/{tg_id}_'

    for key, value in user_location_data.items():
        if value.get('img'):
            if os.path.exists(path + key + '.png'):
                os.remove(path + key + '.png')

    user_location.data = '{}'

    return True


@session_action
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

    user_location.data = json.dumps(new_data)

    path = utils.get_project_path() + f'data/imgs/{tg_id}_'

    if removed_data.get('img'):
        if os.path.exists(path + key + '.png'):
            os.remove(path + key + '.png')

    return True

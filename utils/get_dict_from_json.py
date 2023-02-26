import asyncio
import json
import os

__all__ = ['get_dict_from_json']
json_encoding = 'utf-8'


def get_dict_from_json(path_to_json_file: str):

    if not os.path.exists(path_to_json_file):
        return dict()

    with open(path_to_json_file, mode='r', encoding=json_encoding) as json_file:
        cur_json = json.loads(json_file.read())

    return cur_json

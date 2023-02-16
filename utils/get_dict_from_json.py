import json
import os

from typing import (Dict, Any)

__all__ = ['get_dict_from_json']


def get_dict_from_json(path_to_json_file: str) -> Dict:
    if not os.path.exists(path_to_json_file):
        return {}

    with open(path_to_json_file, mode='r', encoding='utf-8') as json_file:
        cur_json = json.loads(json_file.read())

    return cur_json

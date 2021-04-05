__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2020/05/19'

import os
import json
from typing import Any, AnyStr


def save_file(data: AnyStr, path: str) -> None:
    """
    Save data to a file.
    :param data: data to save.
    :param path: string with the path to an output file.
    """
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    with open(path, 'w', encoding="utf8") as f:
        f.write(data)


def save_json(data: Any, path: str) -> None:
    """
    Save data to a JSON file.
    :param data: data to save.
    :param path: string with the path to an output file.
    """
    save_file(json.dumps(data, indent=4), path)

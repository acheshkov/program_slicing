__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/23'

from typing import Tuple

CDG_CONTENT_TYPE_FUNCTION = "FUNCTION"
CDG_CONTENT_TYPE_VARIABLE = "VARIABLE"
CDG_CONTENT_TYPE_ASSIGNMENT = "ASSIGNMENT"
CDG_CONTENT_TYPE_CALL = "CALL"
CDG_CONTENT_TYPE_STATEMENTS = "STATEMENTS"
CDG_CONTENT_TYPE_BRANCH = "BRANCH"
CDG_CONTENT_TYPE_LOOP = "LOOP"
CDG_CONTENT_TYPE_BREAK = "BREAK"
CDG_CONTENT_TYPE_GOTO = "GOTO"
CDG_CONTENT_TYPE_OBJECT = "OBJECT"
CDG_CONTENT_TYPE_EXIT = "EXIT"


class CDGContent:
    def __init__(self, label: str, content_type: str, ids: Tuple[int, int]):
        self.label: str = label
        self.content_type: int = content_type
        self.ids: Tuple[int, int] = ids

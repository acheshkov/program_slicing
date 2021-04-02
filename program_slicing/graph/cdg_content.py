__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/23'

from typing import Tuple, Optional

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
    def __init__(
            self,
            ast_class: str,
            content_type: str,
            line_range: Tuple[int, int],
            name: Optional[str] = None):
        self.ast_class: str = ast_class
        self.content_type: int = content_type
        self.line_range: Tuple[int, int] = line_range
        self.name: Optional[str] = name

__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/23'

from typing import Tuple, Optional

STATEMENT_TYPE_FUNCTION = "FUNCTION"
STATEMENT_TYPE_VARIABLE = "VARIABLE"
STATEMENT_TYPE_ASSIGNMENT = "ASSIGNMENT"
STATEMENT_TYPE_CALL = "CALL"
STATEMENT_TYPE_STATEMENTS = "STATEMENTS"
STATEMENT_TYPE_BRANCH = "BRANCH"
STATEMENT_TYPE_LOOP = "LOOP"
STATEMENT_TYPE_GOTO = "GOTO"
STATEMENT_TYPE_OBJECT = "OBJECT"
STATEMENT_TYPE_EXIT = "EXIT"


class Statement:

    def __init__(
            self,
            ast_class: str,
            statement_type: str,
            start_point: Tuple[int, int],
            end_point: Tuple[int, int],
            name: Optional[str] = None):
        self.ast_class: str = ast_class
        self.statement_type: str = statement_type
        self.start_point: Tuple[int, int] = start_point
        self.end_point: Tuple[int, int] = end_point
        self.name: Optional[str] = name

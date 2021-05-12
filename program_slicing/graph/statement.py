__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/23'

from typing import Tuple, Optional, Set
from enum import Enum


class StatementType(Enum):
    function = "FUNCTION"
    variable = "VARIABLE"
    assignment = "ASSIGNMENT"
    call = "CALL"
    statements = "STATEMENTS"
    branch = "BRANCH"
    loop = "LOOP"
    goto = "GOTO"
    object = "OBJECT"
    exit = "EXIT"


class Statement:

    def __init__(
            self,
            statement_type: StatementType,
            start_point: Tuple[int, int],
            end_point: Tuple[int, int],
            affected_by: Set[str] = None,
            name: Optional[str] = None,
            meta: str = None):
        self.meta: str = meta
        self.statement_type: StatementType = statement_type
        self.start_point: Tuple[int, int] = start_point
        self.end_point: Tuple[int, int] = end_point
        self.affected_by: Set[str] = set() if affected_by is None else affected_by
        self.name: Optional[str] = name

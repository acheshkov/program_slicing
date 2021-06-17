__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/23'

from typing import Tuple, Optional, Set
from enum import Enum


class StatementType(Enum):
    FUNCTION = "FUNCTION"
    VARIABLE = "VARIABLE"
    ASSIGNMENT = "ASSIGNMENT"
    CALL = "CALL"
    SCOPE = "SCOPE"
    BRANCH = "BRANCH"
    LOOP = "LOOP"
    GOTO = "GOTO"
    UNKNOWN = "UNKNOWN"
    EXIT = "EXIT"


StatementLineNumber = int
StatementColumnNumber = int
VariableName = str


class Statement:

    def __init__(
            self,
            statement_type: StatementType,
            start_point: Tuple[StatementLineNumber, StatementColumnNumber],
            end_point: Tuple[StatementLineNumber, StatementColumnNumber],
            affected_by: Set[VariableName] = None,
            name: Optional[VariableName] = None,
            ast_node_type: str = None):
        self.__statement_type: StatementType = statement_type
        self.__start_point: Tuple[StatementLineNumber, StatementColumnNumber] = start_point
        self.__end_point: Tuple[StatementLineNumber, StatementColumnNumber] = end_point
        self.__affected_by: Set[VariableName] = set() if affected_by is None else affected_by
        self.__name: Optional[VariableName] = name
        self.__ast_node_type: str = ast_node_type

    @property
    def statement_type(self) -> StatementType:
        return self.__statement_type

    @property
    def start_point(self) -> Tuple[StatementLineNumber, StatementColumnNumber]:
        return self.__start_point

    @property
    def end_point(self) -> Tuple[StatementLineNumber, StatementColumnNumber]:
        return self.__end_point

    @property
    def affected_by(self) -> Set[VariableName]:
        return self.__affected_by

    @property
    def name(self) -> Optional[VariableName]:
        return self.__name

    @property
    def ast_node_type(self) -> str:
        return self.__ast_node_type

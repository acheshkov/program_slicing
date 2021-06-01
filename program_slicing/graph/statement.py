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
        self.ast_node_type: str = ast_node_type
        self.statement_type: StatementType = statement_type
        self.start_point: Tuple[StatementLineNumber, StatementColumnNumber] = start_point
        self.end_point: Tuple[StatementLineNumber, StatementColumnNumber] = end_point
        self.affected_by: Set[VariableName] = set() if affected_by is None else affected_by
        self.name: Optional[VariableName] = name

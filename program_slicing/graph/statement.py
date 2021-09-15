__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/23'

from typing import Optional, Set
from enum import Enum

from program_slicing.graph.point import Point


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


VariableName = str


class Statement:

    def __init__(
            self,
            statement_type: StatementType,
            start_point: Point,
            end_point: Point,
            affected_by: Set[VariableName] = None,
            name: Optional[VariableName] = None,
            ast_node_type: str = None,
            start_byte: int = None,
            end_byte: int = None) -> None:
        self.__statement_type: StatementType = statement_type
        self.__start_point: Point = start_point
        self.__end_point: Point = end_point
        self.__affected_by: Set[VariableName] = set() if affected_by is None else affected_by
        self.__name: Optional[VariableName] = name
        self.__ast_node_type: str = ast_node_type
        self.__start_byte = start_byte
        self.__end_byte = end_byte

    def __repr__(self) -> str:
        return \
            "Statement(" \
            "statement_type={statement_type}, " \
            "ast_node_type={ast_node_type}, " \
            "name={name}, " \
            "affected_by={affected_by}, " \
            "start_point={start_point}, " \
            "end_point={end_point})".format(
                statement_type=self.__statement_type,
                ast_node_type=self.__ast_node_type,
                name=None if self.__name is None else "'" + self.__name + "'",
                affected_by=self.__affected_by,
                start_point=self.__start_point,
                end_point=self.__end_point
            )

    def __str__(self) -> str:
        if not self.__name:
            short_name = ""
        else:
            short_name = "'" + (self.__name if len(self.__name) < 30 else (self.__name[0:27] + "...")) + "' "
        affected_by = "affected by variables " + str(self.__affected_by) + " " if self.__affected_by else ""
        return \
            "{statement_type}({ast_node_type}) " \
            "{name}" \
            "{affected_by}" \
            "position in code: {start_point} - {end_point}".format(
                statement_type=self.__statement_type.value,
                ast_node_type=self.__ast_node_type,
                name=short_name,
                affected_by=affected_by,
                start_point=self.__start_point,
                end_point=self.__end_point
            )

    @property
    def start_byte(self):
        return self.__start_byte

    @property
    def end_byte(self):
        return self.__end_byte

    @property
    def statement_type(self) -> StatementType:
        return self.__statement_type

    @property
    def start_point(self) -> Point:
        return self.__start_point

    @property
    def end_point(self) -> Point:
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

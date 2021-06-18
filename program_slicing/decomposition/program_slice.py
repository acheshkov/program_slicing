__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/05/20'

from enum import Enum
from typing import List, Tuple, Dict, Optional, Iterable

from program_slicing.graph.statement import Statement, StatementType, StatementColumnNumber, StatementLineNumber


class RangeType(Enum):
    FULL = "FULL"
    BOUNDS = "BOUNDS"
    BEGINNING = "BEGINNING"


class ProgramSlice:

    def __init__(self, __source_lines: List[str]):
        self.__source_lines: List[str] = __source_lines
        self.__minimum_column: Optional[StatementColumnNumber] = None
        self.__start_point: Optional[Tuple[StatementLineNumber, StatementColumnNumber]] = None
        self.__end_point: Optional[Tuple[StatementLineNumber, StatementColumnNumber]] = None
        self.__start_points: Dict[StatementLineNumber, StatementColumnNumber] = {}
        self.__end_points: Dict[StatementLineNumber, StatementColumnNumber] = {}
        self.__code = None
        self.__lines = None
        self.__ranges = None
        self.__external_scope = None

    def __str__(self):
        return self.code

    @property
    def source_lines(self) -> List[str]:
        """
        Get source code lines.
        :return: string with the corresponding source code.
        """
        return self.__source_lines

    @property
    def code(self) -> str:
        """
        Get source code for the current slice.
        :return: string with the corresponding source code.
        """
        if self.__code is None:
            self.__code = "\n".join(self.lines)
        return self.__code

    @property
    def lines(self) -> List[str]:
        """
        Get source code lines for the current slice.
        :return: list of strings with the corresponding source code lines.
        """
        if self.__lines is None:
            self.__lines = [
                self.__source_lines[start_point[0]][start_point[1]: end_point[1]]
                for start_point, end_point in self.ranges
            ]
        return self.__lines

    @property
    def ranges(self) -> List[Tuple[
            Tuple[StatementLineNumber, StatementColumnNumber],
            Tuple[StatementLineNumber, StatementColumnNumber]]]:
        """
        Get ranges of lines and columns for the current slice.
        :return: list of tuples of start and end points (point is a tuple of two integers).
        """
        if self.__ranges is not None:
            return self.__ranges
        self.__ranges = []
        for line_number in sorted(self.__end_points.keys()):
            start_column = self.__start_point[1] if line_number == self.__start_point[0] else (
                min(self.__minimum_column, self.__start_points[line_number]) if line_number in self.__start_points else
                self.__minimum_column)
            end_column = self.__end_points[line_number]
            self.__ranges.append((
                (line_number, min(start_column, end_column)),
                (line_number, end_column)))
        return self.__ranges

    def from_statements(self, statements: Iterable[Statement]) -> 'ProgramSlice':
        """
        Build a slice based on the given Statements.
        If slice has already been built, it will be extended.
        :param statements: an Iterable object of Statements on which the slice should to be based.
        :return: ProgramSlice that corresponds to a given set of Statements.
        """
        for statement in statements:
            self.add_statement(statement)
        return self

    def from_ranges(
            self,
            position_ranges: Iterable[Tuple[
                Tuple[StatementLineNumber, StatementColumnNumber],
                Tuple[StatementLineNumber, StatementColumnNumber]
            ]]) -> 'ProgramSlice':
        """
        Build a slice based on the given ranges of positions in a source code.
        If slice has already been built, it will be extended.
        :param position_ranges: an Iterable object of ranges in the source code on which the slice should to be based.
        :return: ProgramSlice that corresponds to a given set of position ranges.
        """
        for position_range in position_ranges:
            self.add_range(position_range[0], position_range[1], RangeType.FULL)
        return self

    def add_statement(self, statement: Statement) -> None:
        """
        Add a specified Statement to the current slice.
        :param statement: a concrete Statement that should to be presented in a slice.
        """
        range_type = \
            RangeType.BOUNDS if statement.statement_type == StatementType.SCOPE else \
            RangeType.FULL if statement.statement_type == StatementType.UNKNOWN else \
            RangeType.BEGINNING
        start_point = statement.start_point
        end_point = statement.end_point
        if self.__external_scope is not None:
            start_point_out_of_external_scope = \
                start_point[0] < self.__external_scope.start_point[0] or \
                start_point[0] == self.__external_scope.start_point[0] and \
                start_point[1] <= self.__external_scope.start_point[1]
            end_point_out_of_external_scope = \
                end_point[0] > self.__external_scope.end_point[0] or \
                end_point[0] == self.__external_scope.end_point[0] and \
                end_point[1] >= self.__external_scope.end_point[1]
            if start_point_out_of_external_scope or end_point_out_of_external_scope:
                self.add_range(self.__external_scope.start_point, self.__external_scope.end_point, RangeType.BOUNDS)
                self.__external_scope = None
        if statement.statement_type == StatementType.SCOPE and \
                self.__start_point_out_of_bounds(statement.start_point) and \
                self.__end_point_out_of_bounds(statement.end_point):
            self.__external_scope = statement
        else:
            self.add_range(statement.start_point, statement.end_point, range_type)

    def add_range(
            self,
            start_point: Tuple[StatementLineNumber, StatementColumnNumber],
            end_point: Tuple[StatementLineNumber, StatementColumnNumber],
            range_type: RangeType) -> None:
        """
        Add a specified range into the current slice.
        :param start_point: line and column numbers of the first symbol of the slice part.
        :param end_point: line and column of the last symbol that should to be added to the slice.
        :param range_type: all the lines between end and start point will be added to a slice if FULL.
        Only the first and the last lines will be added if BOUNDS.
        Only the first line will be added if BEGINNING.
        """
        self.__code = None
        self.__ranges = None
        self.__lines = None
        self.__update_minimal_column(start_point, end_point)
        if self.__start_point_out_of_bounds(start_point):
            self.__start_point = start_point
        if self.__end_point_out_of_bounds(end_point):
            self.__end_point = end_point
        first_line = start_point[0]
        last_line = end_point[0]
        last_range_line = last_line if range_type == RangeType.FULL else min(last_line, first_line + 1)
        for line_number in range(start_point[0], last_range_line):
            self.__end_points[line_number] = len(self.__source_lines[line_number])
            current_line_start_point = self.__get_start_point_of_line(line_number)
            if current_line_start_point < self.__minimum_column:
                self.__start_points[line_number] = current_line_start_point
        if range_type == RangeType.BEGINNING and last_range_line > first_line:
            return
        if last_line not in self.__end_points:
            self.__end_points[last_line] = end_point[1]
        else:
            self.__end_points[last_line] = max(end_point[1], self.__end_points[last_line])
        last_line_start_point = self.__get_start_point_of_line(last_line)
        if last_line_start_point < self.__minimum_column:
            self.__start_points[last_line] = last_line_start_point

    def __get_start_point_of_line(self, line_number: StatementLineNumber) -> StatementColumnNumber:
        for i, character in enumerate(self.__source_lines[line_number]):
            if character != " " and character != "\t":
                return i

    def __start_point_out_of_bounds(self, start_point: Tuple[StatementLineNumber, StatementColumnNumber]) -> bool:
        return \
            self.__start_point is None or \
            start_point[0] < self.__start_point[0] or \
            start_point[0] == self.__start_point[0] and start_point[1] <= self.__start_point[1]

    def __end_point_out_of_bounds(self, end_point: Tuple[StatementLineNumber, StatementColumnNumber]) -> bool:
        return \
            self.__end_point is None or \
            end_point[0] > self.__end_point[0] or \
            end_point[0] == self.__end_point[0] and end_point[1] >= self.__end_point[1]

    def __update_minimal_column(
            self,
            start_point: Tuple[StatementLineNumber, StatementColumnNumber],
            end_point: Tuple[StatementLineNumber, StatementColumnNumber]) -> None:
        if self.__minimum_column is None:
            self.__minimum_column = max(0, min(start_point[1], end_point[1] - 1))
        elif start_point[1] < self.__minimum_column:
            self.__minimum_column = start_point[1]
        elif end_point[1] < self.__minimum_column:
            self.__minimum_column = max(0, end_point[1] - 1)

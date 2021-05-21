__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/05/20'

from enum import Enum
from typing import List, Tuple, Dict, Optional

from program_slicing.graph.statement import Statement, StatementType


class RangeType(Enum):
    FULL = "FULL"
    BOUNDS = "BOUNDS"
    BEGINNING = "BEGINNING"


class ProgramSlice:

    def __init__(self, code_lines: List[str]):
        self.code_lines: List[str] = code_lines
        self.minimum_column: Optional[int] = None
        self.start_point: Optional[Tuple[int, int]] = None
        self.end_points: Dict[int, int] = {}

    def add_statement(self, statement: Statement) -> None:
        """
        Add a specified Statement to a slice.
        :param statement: a concrete Statement that should to be presented in a slice.
        """
        range_type = \
            RangeType.BOUNDS if statement.statement_type == StatementType.statements else \
            RangeType.FULL if statement.statement_type == StatementType.object else \
            RangeType.BEGINNING
        self.add_range(statement.start_point, statement.end_point, range_type)

    def add_range(self, start_point: Tuple[int, int], end_point: Tuple[int, int], range_type: RangeType) -> None:
        """
        Build source code for the current slice.
        :param start_point: line and column numbers of the first symbol of the slice part.
        :param end_point: line and column of the last symbol that should to be added to the slice.
        :param range_type: all the lines between end and start point will be added to a slice if FULL.
        Only the first and the last lines will be added if BOUNDS.
        Only the first line will be added if BEGINNING.
        """
        if self.minimum_column is None:
            self.minimum_column = max(0, min(start_point[1], end_point[1] - 1))
        elif start_point[1] < self.minimum_column:
            self.minimum_column = start_point[1]
        elif end_point[1] < self.minimum_column:
            self.minimum_column = max(0, end_point[1] - 1)
        if self.start_point is None or \
                start_point[0] < self.start_point[0] or \
                (start_point[0] == self.start_point[0] and start_point[1] < self.start_point[1]):
            self.start_point = start_point
        first_line = start_point[0]
        last_line = end_point[0]
        last_range_line = last_line if range_type == RangeType.FULL else min(last_line, first_line + 1)
        for line_number in range(start_point[0], last_range_line):
            self.end_points[line_number] = len(self.code_lines[line_number])
        if range_type == RangeType.BEGINNING:
            return
        if last_line not in self.end_points:
            self.end_points[last_line] = end_point[1]
        else:
            self.end_points[last_line] = max(end_point[1], self.end_points[last_line])

    def get_slice_code(self) -> str:
        """
        Build source code for the current slice.
        :return: string with the corresponding source code.
        """
        return "\n".join(self.get_slice_lines())

    def get_slice_lines(self) -> List[str]:
        """
        Build source code lines for the current slice.
        :return: list of strings with the corresponding source code lines.
        """
        return [
            self.code_lines[start_point[0]][start_point[1]: end_point[1]]
            for start_point, end_point in self.get_ranges()
        ]

    def get_ranges(self) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """
        Build ranges of lines and columns for the current slice.
        :return: list of tuples of start and end points (point is a tuple of two integers).
        """
        ranges = []
        for line_number in sorted(self.end_points.keys()):
            start_column = self.start_point[1] if line_number == self.start_point[0] else self.minimum_column
            end_column = self.end_points[line_number]
            ranges.append((
                (line_number, min(start_column, end_column)),
                (line_number, end_column)))
        return ranges

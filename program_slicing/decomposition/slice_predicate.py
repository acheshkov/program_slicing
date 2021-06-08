__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/06/03'

from typing import Union, List, Tuple

from program_slicing.decomposition.code_lines_slicer import CodeLinesSlicer
from program_slicing.graph.statement import Statement, StatementLineNumber, StatementColumnNumber


class SlicePredicate:

    def __init__(
            self,
            min_amount_of_lines: int = None,
            max_amount_of_lines: int = None):
        self.__min_amount_of_lines = min_amount_of_lines
        self.__max_amount_of_lines = max_amount_of_lines
        self.__checkers = [
            self.__check_min_amount_of_lines,
            self.__check_max_amount_of_lines
        ]
        self.__program_slice = None

    def __call__(
            self,
            program_slice: Union[
                CodeLinesSlicer,
                List[Statement],
                List[Tuple[
                    Tuple[StatementLineNumber, StatementColumnNumber],
                    Tuple[StatementLineNumber, StatementColumnNumber]]],
                Tuple[Statement, Statement, CodeLinesSlicer],
                Tuple[Statement, Statement, List[Statement]]
            ]):
        if program_slice is None:
            return False
        self.__program_slice = program_slice
        for checker in self.__checkers:
            if not checker():
                return False
        return True

    def __check_min_amount_of_lines(self) -> bool:
        if self.__min_amount_of_lines is None:
            return True
        if self.__get_amount_of_lines(self.__program_slice) < self.__min_amount_of_lines:
            return False
        return True

    def __check_max_amount_of_lines(self) -> bool:
        if self.__max_amount_of_lines is None:
            return True
        if self.__get_amount_of_lines(self.__program_slice) > self.__max_amount_of_lines:
            return False
        return True

    @staticmethod
    def __get_amount_of_lines(program_slice):
        if type(program_slice) is list:
            marked_lines = set()
            for data_obj in program_slice:
                if type(data_obj) is Statement:
                    start_point = data_obj.start_point
                    end_point = data_obj.end_point
                else:
                    start_point, end_point = data_obj
                marked_lines.update({
                    line_number for line_number in range(start_point[0], end_point[0] + 1)
                })
            return len(marked_lines)
        elif type(program_slice) is CodeLinesSlicer:
            return len(program_slice.get_slice_lines())
        elif type(program_slice) is tuple:
            return SlicePredicate.__get_amount_of_lines(program_slice[-1])
        else:
            return -1


def check_slice(
        program_slice: Union[
            CodeLinesSlicer,
            List[Statement],
            List[Tuple[
                Tuple[StatementLineNumber, StatementColumnNumber],
                Tuple[StatementLineNumber, StatementColumnNumber]]],
            Tuple[Statement, Statement, CodeLinesSlicer],
            Tuple[Statement, Statement, List[Statement]]
        ],
        min_amount_of_lines: int = None,
        max_amount_of_lines: int = None) -> bool:
    """
    Check a slice if it matches specified conditions. Slice may be provided by one of the next structures:
     1. CodeLinesSlicer - object that offer to get_slice_lines (list of strings that are presented in the slice).
     2. List of Statements that are presented in the slice.
     3. List of ranges. Each range is a tuple of start and end points. Points are tuples of line and column numbers.
     4. Tuple of function Statement, variable Statement and CodeLinesSlicer.
        This structure will be processed in the same way as a single CodeLinesSlicer.
     5. Tuple of function Statement, variable Statement and a list of Statements.
        This structure will be processed in the same way as a single list of Statements.
    :param program_slice: slice that should to be checked.
    :param min_amount_of_lines: minimal acceptable amount of lines.
    :param max_amount_of_lines: maximal acceptable amount of lines.
    :return: True if slice matches specified conditions.
    """
    return SlicePredicate(
        min_amount_of_lines=min_amount_of_lines,
        max_amount_of_lines=max_amount_of_lines
    )(program_slice)

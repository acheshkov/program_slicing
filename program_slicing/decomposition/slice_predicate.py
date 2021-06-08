__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/06/03'

from typing import Iterable

from program_slicing.graph.statement import Statement


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

    def __call__(self, program_slice: Iterable[Statement]):
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
        marked_lines = set()
        for data_obj in program_slice:
            start_point = data_obj.start_point
            end_point = data_obj.end_point
            marked_lines.update({
                line_number for line_number in range(start_point[0], end_point[0] + 1)
            })
        return len(marked_lines)


def check_slice(
        program_slice: Iterable[Statement],
        min_amount_of_lines: int = None,
        max_amount_of_lines: int = None) -> bool:
    """
    Check a slice if it matches specified conditions. Slice should be provided by set of Statements.
    :param program_slice: slice that should to be checked.
    :param min_amount_of_lines: minimal acceptable amount of lines.
    :param max_amount_of_lines: maximal acceptable amount of lines.
    :return: True if slice matches specified conditions.
    """
    return SlicePredicate(
        min_amount_of_lines=min_amount_of_lines,
        max_amount_of_lines=max_amount_of_lines
    )(program_slice)

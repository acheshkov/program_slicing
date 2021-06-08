__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/06/03'

from typing import Union, List, Tuple

from program_slicing.decomposition.code_lines_slicer import CodeLinesSlicer
from program_slicing.graph.statement import Statement, StatementLineNumber, StatementColumnNumber


class CheckSlice:
    def __init__(
            self,
            data: Union[
                CodeLinesSlicer,
                List[Statement],
                List[Tuple[
                    Tuple[StatementLineNumber, StatementColumnNumber],
                    Tuple[StatementLineNumber, StatementColumnNumber]]]
            ]):
        self.__check = True
        self.data: Union[
            CodeLinesSlicer,
            List[Statement],
            List[Tuple[
                Tuple[StatementLineNumber, StatementColumnNumber],
                Tuple[StatementLineNumber, StatementColumnNumber]]]
        ] = data

    def __bool__(self):
        return self.__check

    def by_min_amount_of_lines(self, min_amount_of_lines: int) -> 'CheckSlice':
        """
        Add or change limits on minimal amount of lines in slice that matches the conditions.
        :param min_amount_of_lines: minimal acceptable amount of lines.
        :return: an original check object.
        """
        if self.__get_amount_of_lines() < min_amount_of_lines:
            self.__check = False
        return self

    def by_max_amount_of_lines(self, max_amount_of_lines: int) -> 'CheckSlice':
        """
        Add or change limits on maximal amount of lines in slice that matches the conditions.
        :param max_amount_of_lines: maximal acceptable amount of lines.
        :return: an original check object.
        """
        if self.__get_amount_of_lines() > max_amount_of_lines:
            self.__check = False
        return self

    def __get_amount_of_lines(self):
        if type(self.data) is list:
            marked_lines = set()
            for data_obj in self.data:
                if type(data_obj) is Statement:
                    start_point = data_obj.start_point
                    end_point = data_obj.end_point
                else:
                    start_point, end_point = data_obj
                marked_lines.update({
                    line_number for line_number in range(start_point[0], end_point[0] + 1)
                })
            return len(marked_lines)
        elif type(self.data) is CodeLinesSlicer:
            return len(self.data.get_slice_lines())
        else:
            return -1


def check_slice(
        data: Union[
            CodeLinesSlicer,
            List[Statement],
            List[Tuple[
                Tuple[StatementLineNumber, StatementColumnNumber],
                Tuple[StatementLineNumber, StatementColumnNumber]]]
        ]) -> CheckSlice:
    """
    Check a slice if it matches specified conditions. Slice may be provided by one of the next structures:
     1. CodeLinesSlicer - object that offer to get_slice_lines (list of strings that are presented in the slice).
     2. List of Statements that are presented in the slice.
     3. List of ranges. Each range is a tuple of start and end points. Points are tuples of line and column numbers.
    :param data: slice that should to be checked.
    :return: an object (that may be casted to bool) with functions that provide possibility to change conditions.
    """
    return CheckSlice(data)

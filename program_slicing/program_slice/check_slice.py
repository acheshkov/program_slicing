__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/06/03'

from typing import Union, List, Tuple

from program_slicing.decomposition.code_lines_slicer import CodeLinesSlicer
from program_slicing.graph.statement import Statement


class CheckSlice:
    def __init__(
            self,
            data: Union[
                CodeLinesSlicer,
                List[Statement],
                List[Tuple[Tuple[int, int], Tuple[int, int]]]
            ]):
        self.__check = True
        self.data: Union[
            CodeLinesSlicer,
            List[Statement],
            List[Tuple[Tuple[int, int], Tuple[int, int]]]
        ] = data

    def __bool__(self):
        return self.__check

    def by_min_amount_of_lines(self, min_amount_of_lines: int) -> 'CheckSlice':
        if self.__get_amount_of_lines() < min_amount_of_lines:
            self.__check = False
        return self

    def by_max_amount_of_lines(self, max_amount_of_lines: int) -> 'CheckSlice':
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
            Tuple[Statement, Statement, CodeLinesSlicer],
            Tuple[Statement, Statement, List[Statement]],
            List[Statement],
            List[Tuple[Tuple[int, int], Tuple[int, int]]]
        ]) -> CheckSlice:
    return CheckSlice(data)

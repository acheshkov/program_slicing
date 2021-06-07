__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/06/01'

from typing import Iterable, Iterator, List, Tuple, Union, Optional

from program_slicing.graph.statement import Statement
from program_slicing.decomposition.code_lines_slicer import CodeLinesSlicer
from program_slicing.utils.check_slice import CheckSlice


class FilterSlices:
    def __init__(
            self,
            data: Iterable[Union[
                CodeLinesSlicer,
                Tuple[Statement, Statement, CodeLinesSlicer],
                Tuple[Statement, Statement, List[Statement]],
                List[Statement],
                List[Tuple[Tuple[int, int], Tuple[int, int]]]
            ]]):
        self.data: Iterator[Union[
            CodeLinesSlicer,
            Tuple[Statement, Statement, CodeLinesSlicer],
            Tuple[Statement, Statement, List[Statement]],
            List[Statement],
            List[Tuple[Tuple[int, int], Tuple[int, int]]]
        ]] = data.__iter__()
        self.min_amount_of_lines: Optional[int] = None
        self.max_amount_of_lines: Optional[int] = None

    def __iter__(self):
        return (data_obj for data_obj in self.data if self.__check(data_obj))

    def by_min_amount_of_lines(self, min_amount_of_lines: int) -> 'FilterSlices':
        self.min_amount_of_lines = min_amount_of_lines
        return self

    def by_max_amount_of_lines(self, max_amount_of_lines: int) -> 'FilterSlices':
        self.max_amount_of_lines = max_amount_of_lines
        return self

    def __check(self, data_obj) -> bool:
        if type(data_obj) is tuple:
            data_obj = data_obj[2]
        check = CheckSlice(data_obj)
        if self.min_amount_of_lines is not None:
            check.by_min_amount_of_lines(self.min_amount_of_lines)
        if self.max_amount_of_lines is not None:
            check.by_max_amount_of_lines(self.max_amount_of_lines)
        if check:
            return data_obj


def filter_slices(
        data: Iterable[Union[
            CodeLinesSlicer,
            Tuple[Statement, Statement, CodeLinesSlicer],
            Tuple[Statement, Statement, List[Statement]],
            List[Statement],
            List[Tuple[Tuple[int, int], Tuple[int, int]]]
        ]]) -> FilterSlices:
    return FilterSlices(data)

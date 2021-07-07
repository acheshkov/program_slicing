__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/06/24'

from typing import Tuple


class Point:

    def __init__(self, line_number: int, column_number: int) -> None:
        self.__line_number: int = line_number
        self.__column_number: int = column_number

    @classmethod
    def from_tuple(cls, point: Tuple[int, int]) -> 'Point':
        return cls(point[0], point[1])

    def __repr__(self) -> str:
        return "Point{}".format(self)

    def __str__(self) -> str:
        return "({}, {})".format(self.__line_number, self.__column_number)

    def __eq__(self, other: 'Point') -> bool:
        return self.__line_number == other.__line_number and self.__column_number == other.__column_number

    def __ne__(self, other: 'Point') -> bool:
        return self.__line_number != other.__line_number or self.__column_number != other.__column_number

    def __lt__(self, other: 'Point') -> bool:
        return \
            self.__line_number < other.__line_number or \
            self.__line_number == other.__line_number and self.__column_number < other.__column_number

    def __le__(self, other: 'Point') -> bool:
        return \
            self.__line_number < other.__line_number or \
            self.__line_number == other.__line_number and self.__column_number <= other.__column_number

    def __gt__(self, other: 'Point') -> bool:
        return \
            self.__line_number > other.__line_number or \
            self.__line_number == other.__line_number and self.__column_number > other.__column_number

    def __ge__(self, other: 'Point') -> bool:
        return \
            self.__line_number > other.__line_number or \
            self.__line_number == other.__line_number and self.__column_number >= other.__column_number

    @property
    def line_number(self) -> int:
        return self.__line_number

    @property
    def column_number(self) -> int:
        return self.__column_number

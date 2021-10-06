__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/23'

from typing import List, Iterator, Optional

from program_slicing.graph.statement import Statement


class BasicBlock:

    def __init__(self, statements: List[Statement] = None) -> None:
        self.__statements: List[Statement] = [] if statements is None else statements

    def __iter__(self) -> Iterator[Statement]:
        return self.__statements.__iter__()

    def __repr__(self) -> str:
        return "BasicBlock{}".format(self)

    def __str__(self) -> str:
        return str(self.__statements)

    @property
    def statements(self) -> List[Statement]:
        return self.__statements

    @property
    def root(self) -> Optional[Statement]:
        return self.__statements[0] if len(self.__statements) > 0 else None

    def append(self, statement: Statement) -> None:
        self.__statements.append(statement)

    def is_empty(self) -> bool:
        return self.root is None

    def split(self, index: int) -> 'BasicBlock':
        new_block = BasicBlock(statements=self.__statements[index:])
        self.__statements = self.__statements[:index]
        return new_block

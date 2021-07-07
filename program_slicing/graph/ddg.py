__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/04/20'

from typing import Set

import networkx

from program_slicing.graph.statement import Statement


class DataDependenceGraph(networkx.DiGraph):

    def __init__(self) -> None:
        super().__init__()
        self.__entry_points: Set[Statement] = set()

    @property
    def entry_points(self) -> Set[Statement]:
        return self.__entry_points

    def add_entry_point(self, root: Statement) -> None:
        self.__entry_points.add(root)

__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/04/22'

from typing import Set

import networkx

from program_slicing.graph.statement import Statement


class ProgramDependenceGraph(networkx.DiGraph):

    def __init__(self):
        super().__init__()
        self.__entry_points: Set[Statement] = set()

    @property
    def entry_points(self) -> Set[Statement]:
        return self.__entry_points

    def add_entry_point(self, root: Statement) -> None:
        self.__entry_points.add(root)

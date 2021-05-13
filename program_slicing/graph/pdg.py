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
        self.entry_points: Set[Statement] = set()

    def get_entry_points(self) -> Set[Statement]:
        return self.entry_points

    def add_entry_point(self, root: Statement) -> None:
        self.entry_points.add(root)

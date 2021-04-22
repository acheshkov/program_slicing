__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/04/20'

from typing import Set

import networkx

from program_slicing.graph.basic_block import BasicBlock


class DataDependenceGraph(networkx.DiGraph):

    def __init__(self):
        super().__init__()
        self.entry_points: Set[BasicBlock] = set()

    def get_entry_points(self) -> Set[BasicBlock]:
        return self.entry_points

    def add_entry_point(self, root: BasicBlock) -> None:
        self.entry_points.add(root)

__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/30'

import networkx
from typing import Set
from program_slicing.graph.cfg_node import CDGNode


class ControlDependenceGraph(networkx.DiGraph):

    def __init__(self):
        super().__init__()
        self.entry_points: Set[CDGNode] = set()

    def get_entry_points(self) -> Set[CDGNode]:
        return self.entry_points

    def add_entry_point(self, root: CDGNode) -> None:
        self.entry_points.add(root)

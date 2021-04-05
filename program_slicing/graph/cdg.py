__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/30'

import networkx
from typing import Set
from program_slicing.graph.cfg_content import CDGContent


class ControlDependenceGraph(networkx.DiGraph):

    def __init__(self):
        super().__init__()
        self.entry_points: Set[CDGContent] = set()

    def get_entry_points(self) -> Set[CDGContent]:
        return self.entry_points

    def add_entry_point(self, root: CDGContent) -> None:
        self.entry_points.add(root)

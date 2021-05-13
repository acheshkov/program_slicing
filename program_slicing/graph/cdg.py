__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/30'

from typing import Set, Dict, List

import networkx

from program_slicing.graph.statement import Statement


class ControlDependenceGraph(networkx.DiGraph):

    def __init__(self):
        super().__init__()
        self.entry_points: Set[Statement] = set()
        self.control_flow: Dict[Statement, List[Statement]] = {}

    def get_entry_points(self) -> Set[Statement]:
        return self.entry_points

    def add_entry_point(self, root: Statement) -> None:
        self.entry_points.add(root)

__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/30'

from typing import Set, Dict, List

import networkx

from program_slicing.graph.basic_block import BasicBlock


class ControlFlowGraph(networkx.DiGraph):

    def __init__(self):
        super().__init__()
        self.entry_points: Set[BasicBlock] = set()
        self.forward_dominance: Dict[BasicBlock, List[BasicBlock]]

    def get_entry_points(self) -> Set[BasicBlock]:
        return self.entry_points

    def add_entry_point(self, root: BasicBlock) -> None:
        self.entry_points.add(root)

__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/30'

from typing import Set, Dict, List

import networkx

from program_slicing.graph.basic_block import BasicBlock


class ControlFlowGraph(networkx.DiGraph):

    def __init__(self) -> None:
        super().__init__()
        self.__entry_points: Set[BasicBlock] = set()
        self.__forward_dominance: Dict[BasicBlock, List[BasicBlock]] = {}

    @property
    def forward_dominance(self) -> Dict[BasicBlock, List[BasicBlock]]:
        return self.__forward_dominance

    @property
    def entry_points(self) -> Set[BasicBlock]:
        return self.__entry_points

    def add_entry_point(self, root: BasicBlock) -> None:
        self.__entry_points.add(root)

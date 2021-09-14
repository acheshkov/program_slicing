__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/30'

from typing import Set, Dict, List

import networkx

from program_slicing.graph.basic_block import BasicBlock
from program_slicing.graph.statement import Statement


class ControlFlowGraph(networkx.DiGraph):

    def __init__(self) -> None:
        super().__init__()
        self.__entry_points: Set[BasicBlock] = set()
        self.__forward_dominance: Dict[BasicBlock, List[BasicBlock]] = {}
        self.__scope_dependency: Dict[Statement, Statement] = {}

    @property
    def entry_points(self) -> Set[BasicBlock]:
        return self.__entry_points

    # @property
    # def forward_dominance(self) -> Dict[BasicBlock, List[BasicBlock]]:
    #     return self.__forward_dominance

    @property
    def scope_dependency(self) -> Dict[Statement, Statement]:
        return self.__scope_dependency

    def add_entry_point(self, root: BasicBlock) -> None:
        self.__entry_points.add(root)

    def set_scope_dependency(self, scope_dependency: Dict[Statement, Statement]) -> None:
        self.__scope_dependency = scope_dependency

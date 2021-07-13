__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/04/20'

from typing import Dict, Set

import networkx

from program_slicing.graph.statement import Statement


class DataDependenceGraph(networkx.DiGraph):

    def __init__(self) -> None:
        super().__init__()
        self.__entry_points: Set[Statement] = set()
        self.__scope_dependency: Dict[Statement, Statement] = {}

    @property
    def entry_points(self) -> Set[Statement]:
        return self.__entry_points

    @property
    def scope_dependency(self) -> Dict[Statement, Statement]:
        return self.__scope_dependency

    def add_entry_point(self, root: Statement) -> None:
        self.__entry_points.add(root)

    def set_scope_dependency(self, scope_dependency: Dict[Statement, Statement]) -> None:
        self.__scope_dependency = scope_dependency

__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/30'

from typing import Set, Dict, List

import networkx

from program_slicing.graph.statement import Statement


class ControlDependenceGraph(networkx.DiGraph):

    def __init__(self) -> None:
        super().__init__()
        self.__entry_points: Set[Statement] = set()
        self.__control_flow: Dict[Statement, List[Statement]] = {}

    @property
    def control_flow(self) -> Dict[Statement, List[Statement]]:
        return self.__control_flow

    @property
    def entry_points(self) -> Set[Statement]:
        return self.__entry_points

    def add_entry_point(self, root: Statement) -> None:
        self.__entry_points.add(root)

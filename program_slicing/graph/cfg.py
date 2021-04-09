__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/30'

from typing import Set, Dict, List

import networkx

from program_slicing.graph.cfg_node import CFGNode


class ControlFlowGraph(networkx.DiGraph):

    def __init__(self):
        super().__init__()
        self.entry_points: Set[CFGNode] = set()
        self.forward_dominance: Dict[CFGNode, List[CFGNode]]

    def get_entry_points(self) -> Set[CFGNode]:
        return self.entry_points

    def add_entry_point(self, root: CFGNode) -> None:
        self.entry_points.add(root)

    def add_node(self, node: CFGNode, **attr):
        super().add_node(node, node=node)

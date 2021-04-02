__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/30'

import networkx
from typing import Set
from program_slicing.graph.cfg_content import CFGContent


class ControlFlowGraph(networkx.DiGraph):

    def __init__(self):
        super().__init__()
        self.roots: Set[CFGContent] = set()

    def get_roots(self) -> Set[CFGContent]:
        return self.roots

    def add_root(self, root: CFGContent) -> None:
        self.roots.add(root)

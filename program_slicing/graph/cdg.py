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
        self.roots: Set[CDGContent] = set()

    def get_roots(self) -> Set[CDGContent]:
        return self.roots

    def add_root(self, root: CDGContent) -> None:
        self.roots.add(root)

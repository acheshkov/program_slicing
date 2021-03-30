__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/23'

from typing import Set, List
from program_slicing.parse.node import Node


class Block:
    def __init__(self, nodes: List[Node] = None, children: Set['Block'] = None, parents: Set['Block'] = None):
        self.nodes: List[Node] = [] if nodes is None else nodes
        self.children: Set['Block'] = set() if children is None else children
        for child in self.children:
            child.parents.add(self)
        self.parents: Set['Block'] = set() if parents is None else parents
        for parent in self.parents:
            parent.children.add(self)

    def append(self, node: Node) -> None:
        self.nodes.append(node)

    def add_child(self, child: 'Block') -> None:
        if child is not None:
            self.children.add(child)
            child.parents.add(self)

    def get_root(self) -> Node:
        return self.nodes[0] if len(self.nodes) > 0 else None

    def get_cdg_parent(self) -> Node:
        root = self.get_root()
        return None if root is None else root.parent

    def get_cfg_parents(self) -> Set['Block']:
        return self.parents

    def is_empty(self) -> bool:
        return self.get_root() is None

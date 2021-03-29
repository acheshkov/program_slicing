__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/23'

from typing import List, Tuple

NODE_TYPE_FUNCTION = "FUNCTION"
NODE_TYPE_VARIABLE = "VARIABLE"
NODE_TYPE_ASSIGNMENT = "ASSIGNMENT"
NODE_TYPE_CALL = "CALL"
NODE_TYPE_STATEMENTS = "STATEMENTS"
NODE_TYPE_BRANCH = "BRANCH"
NODE_TYPE_LOOP = "LOOP"
NODE_TYPE_BREAK = "BREAK"
NODE_TYPE_GOTO = "GOTO"
NODE_TYPE_OBJECT = "OBJECT"
NODE_TYPE_EXIT = "EXIT"


class Node:
    def __init__(
            self,
            label: str,
            node_type: str,
            ids: Tuple[int, int],
            parent: 'Node' = None,
            children: List['Node'] = None):
        self.children: List['Node'] = [] if children is None else children
        for child in self.children:
            child.parent = self
        self.parent: 'Node' = parent
        self.label: str = label
        self.node_type: int = node_type
        self.ids: List[int] = ids

    def append(self, node: 'Node') -> None:
        self.children.append(node)
        node.parent = self

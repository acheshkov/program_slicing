__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/23'

from typing import Tuple, Optional

CDG_NODE_TYPE_FUNCTION = "FUNCTION"
CDG_NODE_TYPE_VARIABLE = "VARIABLE"
CDG_NODE_TYPE_ASSIGNMENT = "ASSIGNMENT"
CDG_NODE_TYPE_CALL = "CALL"
CDG_NODE_TYPE_STATEMENTS = "STATEMENTS"
CDG_NODE_TYPE_BRANCH = "BRANCH"
CDG_NODE_TYPE_LOOP = "LOOP"
CDG_NODE_TYPE_BREAK = "BREAK"
CDG_NODE_TYPE_GOTO = "GOTO"
CDG_NODE_TYPE_OBJECT = "OBJECT"
CDG_NODE_TYPE_EXIT = "EXIT"


class CDGNode:
    def __init__(
            self,
            ast_class: str,
            node_type: str,
            line_range: Tuple[int, int],
            name: Optional[str] = None):
        self.ast_class: str = ast_class
        self.node_type: int = node_type
        self.line_range: Tuple[int, int] = line_range
        self.name: Optional[str] = name

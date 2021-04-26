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
CDG_NODE_TYPE_GOTO = "GOTO"
CDG_NODE_TYPE_OBJECT = "OBJECT"
CDG_NODE_TYPE_EXIT = "EXIT"


class CDGNode:

    def __init__(
            self,
            ast_class: str,
            node_type: str,
            start_point: Tuple[int, int],
            end_point: Tuple[int, int],
            name: Optional[str] = None):
        self.ast_class: str = ast_class
        self.node_type: str = node_type
        self.start_point: Tuple[int, int] = start_point
        self.end_point: Tuple[int, int] = end_point
        self.name: Optional[str] = name

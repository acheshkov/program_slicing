__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/23'

from typing import List, Optional
from program_slicing.graph.cdg_node import CDGNode


class CFGNode:
    def __init__(self, content: List[CDGNode] = None):
        self.content: List[CDGNode] = [] if content is None else content

    def append(self, node: CDGNode) -> None:
        self.content.append(node)

    def get_root(self) -> Optional[CDGNode]:
        return self.content[0] if len(self.content) > 0 else None

    def get_content(self) -> List[CDGNode]:
        return self.content

    def is_empty(self) -> bool:
        return self.get_root() is None

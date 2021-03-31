__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/23'

from typing import Dict
from program_slicing.parse.node import Node
from program_slicing.parse.block import Block


class ControlGraph:
    def __init__(self, control_graph: 'ControlGraph' = None):
        self.root: Node = None if control_graph is None else control_graph.root
        self.block: Dict[Node: Block] = {} if control_graph is None else control_graph.block

    def get_root_node(self):
        return self.root

    def get_root_blocks(self):
        pass

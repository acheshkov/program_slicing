__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/23'

from typing import Dict, Set
from program_slicing.parser.node import Node
from program_slicing.parser.block import Block


class ControlGraph:
    def __init__(self):
        self.root: Node = None
        self.block: Dict[Node: Block] = {}
        self.dom: Dict[Block: Set[Block]] = {}
        self.reach: Dict[Block: Set[Block]] = {}

    def get_dom(self, block: Block) -> Set[Block]:
        if block in self.dom:
            return self.dom[block]
        dom = set()
        # TODO: There should to be implemented fulfill of the dom
        self.dom[block] = dom
        return dom

    def get_reach(self, block: Block) -> Set[Block]:
        if block in self.reach:
            return self.reach[block]
        reach = set()
        # TODO: There should to be implemented fulfill of the reach
        self.reach[block] = reach
        return reach

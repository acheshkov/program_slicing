__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/30'

from typing import Dict, Set
from program_slicing.parse.cg import ControlGraph
from program_slicing.parse.block import Block


class ControlFlowGraph(ControlGraph):

    def __init__(self, cg: ControlGraph = None):
        super().__init__(cg)
        self.reach: Dict[Block: Set[Block]] = {}

    def get_reach(self, block: Block) -> Set[Block]:
        if block in self.reach:
            return self.reach[block]
        reach = set()
        # TODO: There should to be implemented fulfill of the reach
        self.reach[block] = reach
        return reach

__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/23'

import networkx
from typing import Dict, Optional, Union, Tuple
from program_slicing.graph.parse import parse
from program_slicing.graph.cdg import ControlDependenceGraph
from program_slicing.graph.cfg import ControlFlowGraph
from program_slicing.graph.cdg_content import CDGContent
from program_slicing.graph.cfg_content import CFGContent
from program_slicing.graph.convert.cdg import to_cfg
from program_slicing.graph.convert.cfg import to_cdg


class ProgramGraphsManager:
    def __init__(self, source: Union[Tuple[str, str], ControlDependenceGraph, ControlFlowGraph, None] = None):
        if type(source) is tuple:
            self.init_by_source_code(source_code=source[0], lang=source[1])
        if type(source) is ControlDependenceGraph:
            self.init_by_control_dependence_graph(source)
        elif type(source) is ControlFlowGraph:
            self.init_by_control_flow_graph(source)
        else:
            self.cdg: ControlDependenceGraph = ControlDependenceGraph()
            self.cfg: ControlFlowGraph = ControlFlowGraph()
            self.simple_block: Dict[CDGContent: CFGContent] = {}

    def get_control_dependence_graph(self) -> ControlDependenceGraph:
        return self.cdg

    def get_control_flow_graph(self) -> ControlFlowGraph:
        return self.cfg

    def get_simple_block(self, node: CDGContent) -> Optional[CFGContent]:
        return self.simple_block.get(node, None)

    def init_by_source_code(self, source_code: str, lang: str) -> None:
        self.init_by_control_dependence_graph(parse.control_dependence_graph(source_code, lang))

    def init_by_control_dependence_graph(self, cdg: ControlDependenceGraph) -> None:
        self.cdg = cdg
        self.cfg = to_cfg(cdg)
        self.__build_dependencies()

    def init_by_control_flow_graph(self, cfg: ControlFlowGraph) -> None:
        self.cdg = to_cdg(cfg)
        self.cfg = cfg
        self.__build_dependencies()

    def __build_dependencies(self) -> None:
        self.simple_block.clear()
        for block in networkx.algorithms.traversal.dfs_tree(self.cdg):
            for node in block.get_content():
                self.simple_block[node] = block

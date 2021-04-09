__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/23'

from typing import Dict, Optional, Set

import networkx

from program_slicing.graph.parse import parse
from program_slicing.graph.cdg import ControlDependenceGraph
from program_slicing.graph.cfg import ControlFlowGraph
from program_slicing.graph.cdg_node import CDGNode
from program_slicing.graph.cfg_node import CFGNode
from program_slicing.graph import convert


class ProgramGraphsManager:

    def __init__(self, source_code: str = None, lang: str = None):
        self.cdg: ControlDependenceGraph = ControlDependenceGraph()
        self.cfg: ControlFlowGraph = ControlFlowGraph()
        self.simple_block: Dict[CDGNode, CFGNode] = {}
        self.dom_blocks: Dict[CFGNode, Set[CFGNode]] = {}
        self.reach_blocks: Dict[CFGNode, Set[CFGNode]] = {}
        if source_code is not None and lang is not None:
            self.init_by_source_code(source_code=source_code, lang=lang)

    @classmethod
    def from_control_dependence_graph(cls, graph: ControlDependenceGraph):
        result = cls()
        result.init_by_control_dependence_graph(graph)
        return result

    @classmethod
    def from_control_flow_graph(cls, graph: ControlFlowGraph):
        result = cls()
        result.init_by_control_flow_graph(graph)
        return result

    def get_control_dependence_graph(self) -> ControlDependenceGraph:
        return self.cdg

    def get_control_flow_graph(self) -> ControlFlowGraph:
        return self.cfg

    def get_simple_block(self, node: CDGNode) -> Optional[CFGNode]:
        return self.simple_block.get(node, None)

    def get_dom_blocks(self, block: CFGNode) -> Set[CFGNode]:
        if block in self.dom_blocks:
            return self.dom_blocks[block]
        result = set()
        for node in networkx.algorithms.dominating_set(self.cdg, block.get_root()):
            current_block = self.get_simple_block(node)
            if current_block is not None:
                result.add(self.get_simple_block(node))
        self.dom_blocks[block] = result
        return result

    def get_reach_blocks(self, block: CFGNode) -> Set[CFGNode]:
        return self.__build_reach_blocks(block)

    def init_by_source_code(self, source_code: str, lang: str) -> None:
        self.init_by_control_dependence_graph(parse.control_dependence_graph(source_code, lang))

    def init_by_control_dependence_graph(self, cdg: ControlDependenceGraph) -> None:
        self.cdg = cdg
        self.cfg = convert.cdg.to_cfg(cdg)
        self.__build_dependencies()

    def init_by_control_flow_graph(self, cfg: ControlFlowGraph) -> None:
        self.cdg = convert.cfg.to_cdg(cfg)
        self.cfg = cfg
        self.__build_dependencies()

    def __build_dependencies(self) -> None:
        self.simple_block.clear()
        for block in networkx.algorithms.traversal.dfs_tree(self.cfg):
            for node in block.get_content():
                self.simple_block[node] = block

    def __build_reach_blocks(self, block: CFGNode, visited_nodes: Set[CFGNode] = None) -> Set[CFGNode]:
        if block in self.reach_blocks:
            return self.reach_blocks[block]
        if visited_nodes is None:
            visited_nodes = set()
        visited_nodes.add(block)
        result = set()
        for child in self.cfg.successors(block):
            if child not in visited_nodes:
                result += self.__build_reach_blocks(child, visited_nodes)
        self.reach_blocks[block] = result
        return result

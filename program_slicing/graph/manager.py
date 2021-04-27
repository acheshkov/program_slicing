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
from program_slicing.graph.ddg import DataDependenceGraph
from program_slicing.graph.pdg import ProgramDependenceGraph
from program_slicing.graph.statement import Statement
from program_slicing.graph.basic_block import BasicBlock
from program_slicing.graph import convert


class ProgramGraphsManager:

    def __init__(self, source_code: str = None, lang: str = None):
        self.cdg: ControlDependenceGraph = ControlDependenceGraph()
        self.cfg: ControlFlowGraph = ControlFlowGraph()
        self.ddg: DataDependenceGraph = DataDependenceGraph()
        self.pdg: ProgramDependenceGraph = ProgramDependenceGraph()
        self.basic_block: Dict[Statement, BasicBlock] = {}
        self.dom_blocks: Dict[BasicBlock, Set[BasicBlock]] = {}
        self.reach_blocks: Dict[BasicBlock, Set[BasicBlock]] = {}
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

    @classmethod
    def from_data_dependence_graph(cls, graph: DataDependenceGraph):
        result = cls()
        result.init_by_data_dependence_graph(graph)
        return result

    @classmethod
    def from_program_dependence_graph(cls, graph: ProgramDependenceGraph):
        result = cls()
        result.init_by_program_dependence_graph(graph)
        return result

    def get_control_dependence_graph(self) -> ControlDependenceGraph:
        return self.cdg

    def get_control_flow_graph(self) -> ControlFlowGraph:
        return self.cfg

    def get_data_dependence_graph(self) -> DataDependenceGraph:
        return self.ddg

    def get_program_dependence_graph(self) -> ProgramDependenceGraph:
        return self.pdg

    def get_basic_block(self, statement: Statement) -> Optional[BasicBlock]:
        return self.basic_block.get(statement, None)

    def get_boundary_blocks_for_statement(self, statement: Statement) -> Set[BasicBlock]:
        block = self.get_basic_block(statement)
        return self.get_boundary_blocks(block)

    def get_dominated_blocks(self, block: BasicBlock) -> Set[BasicBlock]:
        if block in self.dom_blocks:
            return self.dom_blocks[block]
        result = set()
        root = block.get_root()
        if root is None:
            return result
        predecessors = [predecessor for predecessor in self.cdg.predecessors(root)]
        if len(predecessors) == 0:
            predecessors = [root]
        for root in predecessors:
            for statement in networkx.algorithms.bfs_tree(self.cdg, root):
                if statement == root:
                    continue
                current_block = self.get_basic_block(statement)
                if current_block is not None:
                    result.add(current_block)
        self.dom_blocks[block] = result
        return result

    def get_reach_blocks(self, block: BasicBlock) -> Set[BasicBlock]:
        return self.__build_reach_blocks(block)

    def get_boundary_blocks(self, block: BasicBlock) -> Set[BasicBlock]:
        return self.get_dominated_blocks(block).intersection(self.get_reach_blocks(block))

    def init_by_source_code(self, source_code: str, lang: str) -> None:
        self.init_by_control_dependence_graph(parse.control_dependence_graph(source_code, lang))

    def init_by_control_dependence_graph(self, cdg: ControlDependenceGraph) -> None:
        self.cdg = cdg
        self.cfg = convert.cdg.to_cfg(cdg)
        self.ddg = convert.cdg.to_ddg(cdg)
        self.pdg = convert.cdg.to_pdg(cdg)
        self.__build_dependencies()

    def init_by_control_flow_graph(self, cfg: ControlFlowGraph) -> None:
        self.cdg = convert.cfg.to_cdg(cfg)
        self.cfg = cfg
        self.ddg = convert.cfg.to_ddg(cfg)
        self.pdg = convert.cfg.to_pdg(cfg)
        self.__build_dependencies()

    def init_by_data_dependence_graph(self, ddg: DataDependenceGraph) -> None:
        self.cdg = convert.ddg.to_cdg(ddg)
        self.cfg = convert.ddg.to_cfg(ddg)
        self.ddg = ddg
        self.pdg = convert.ddg.to_pdg(ddg)
        self.__build_dependencies()

    def init_by_program_dependence_graph(self, pdg: ProgramDependenceGraph) -> None:
        self.cdg = convert.pdg.to_cdg(pdg)
        self.cfg = convert.pdg.to_cfg(pdg)
        self.ddg = convert.pdg.to_ddg(pdg)
        self.pdg = pdg
        self.__build_dependencies()

    def __build_dependencies(self) -> None:
        self.basic_block.clear()
        for block in networkx.algorithms.traversal.dfs_tree(self.cfg):
            for statement in block.get_statements():
                self.basic_block[statement] = block

    def __build_reach_blocks(self, block: BasicBlock, visited_blocks: Set[BasicBlock] = None) -> Set[BasicBlock]:
        if block in self.reach_blocks:
            return self.reach_blocks[block]
        if visited_blocks is None:
            visited_blocks = set()
        visited_blocks.add(block)
        result = {block}
        for child in self.cfg.successors(block):
            if child not in visited_blocks:
                result.update(self.__build_reach_blocks(child, visited_blocks))
        self.reach_blocks[block] = result
        visited_blocks.remove(block)
        return result

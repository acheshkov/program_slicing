__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/23'

from typing import Dict, Optional, Set, List

import networkx

from program_slicing.graph.parse import parse
from program_slicing.graph.cdg import ControlDependenceGraph
from program_slicing.graph.cfg import ControlFlowGraph
from program_slicing.graph.ddg import DataDependenceGraph
from program_slicing.graph.pdg import ProgramDependenceGraph
from program_slicing.graph.statement import Statement, StatementType
from program_slicing.graph.basic_block import BasicBlock
from program_slicing.graph import convert


class ProgramGraphsManager:

    def __init__(self, source_code: str = None, lang: str = None) -> None:
        self.__cdg: ControlDependenceGraph = ControlDependenceGraph()
        self.__cfg: ControlFlowGraph = ControlFlowGraph()
        self.__ddg: DataDependenceGraph = DataDependenceGraph()
        self.__pdg: ProgramDependenceGraph = ProgramDependenceGraph()
        self.__basic_block: Dict[Statement, BasicBlock] = {}
        self.__dom_blocks: Dict[BasicBlock, Set[BasicBlock]] = {}
        self.__reach_blocks: Dict[BasicBlock, Set[BasicBlock]] = {}
        self.__scope_dependency: Dict[Statement, Statement] = {}
        self.__main_statements: List[Statement] = []
        if source_code is not None and lang is not None:
            self.init_by_source_code(source_code=source_code, lang=lang)

    @classmethod
    def from_control_dependence_graph(cls, graph: ControlDependenceGraph) -> 'ProgramGraphsManager':
        result = cls()
        result.init_by_control_dependence_graph(graph)
        return result

    @classmethod
    def from_control_flow_graph(cls, graph: ControlFlowGraph) -> 'ProgramGraphsManager':
        result = cls()
        result.init_by_control_flow_graph(graph)
        return result

    @classmethod
    def from_data_dependence_graph(cls, graph: DataDependenceGraph) -> 'ProgramGraphsManager':
        result = cls()
        result.init_by_data_dependence_graph(graph)
        return result

    @classmethod
    def from_program_dependence_graph(cls, graph: ProgramDependenceGraph) -> 'ProgramGraphsManager':
        result = cls()
        result.init_by_program_dependence_graph(graph)
        return result

    def get_control_dependence_graph(self) -> ControlDependenceGraph:
        return self.__cdg

    def get_control_flow_graph(self) -> ControlFlowGraph:
        return self.__cfg

    def get_data_dependence_graph(self) -> DataDependenceGraph:
        return self.__ddg

    def get_program_dependence_graph(self) -> ProgramDependenceGraph:
        return self.__pdg

    def get_scope_statement(self, statement: Statement) -> Optional[Statement]:
        return self.__scope_dependency.get(statement, None)

    def get_basic_block(self, statement: Statement) -> Optional[BasicBlock]:
        return self.__basic_block.get(statement, None)

    def get_boundary_blocks_for_statement(self, statement: Statement) -> Set[BasicBlock]:
        block = self.get_basic_block(statement)
        return self.get_boundary_blocks(block)

    def get_dominated_blocks(self, block: BasicBlock) -> Set[BasicBlock]:
        if block in self.__dom_blocks:
            return self.__dom_blocks[block]
        result = {block}
        root = block.root
        if root is None:
            return result
        predecessors = [predecessor for predecessor in self.__cdg.predecessors(root)]
        if len(predecessors) == 0:
            predecessors = [root]
        for root in predecessors:
            for statement in networkx.algorithms.bfs_tree(self.__cdg, root):
                if statement == root:
                    continue
                current_block = self.get_basic_block(statement)
                if current_block is not None:
                    result.add(current_block)
        self.__dom_blocks[block] = result
        return result

    def get_reach_blocks(self, block: BasicBlock) -> Set[BasicBlock]:
        return self.__build_reach_blocks(block)

    def get_boundary_blocks(self, block: BasicBlock) -> Set[BasicBlock]:
        boundary_blocks = set()
        for basic_block in self.__cfg:
            if block in self.get_dominated_blocks(basic_block).intersection(self.get_reach_blocks(basic_block)):
                boundary_blocks.add(basic_block)
        return boundary_blocks

    def init_by_source_code(self, source_code: str, lang: str) -> None:
        self.init_by_control_dependence_graph(parse.control_dependence_graph(source_code, lang))

    def init_by_control_dependence_graph(self, cdg: ControlDependenceGraph) -> None:
        self.__cdg = cdg
        self.__cfg = convert.cdg.to_cfg(cdg)
        self.__ddg = convert.cdg.to_ddg(cdg)
        self.__pdg = convert.cdg.to_pdg(cdg)
        self.__build_dependencies()

    def init_by_control_flow_graph(self, cfg: ControlFlowGraph) -> None:
        self.__cdg = convert.cfg.to_cdg(cfg)
        self.__cfg = cfg
        self.__ddg = convert.cfg.to_ddg(cfg)
        self.__pdg = convert.cfg.to_pdg(cfg)
        self.__build_dependencies()

    def init_by_data_dependence_graph(self, ddg: DataDependenceGraph) -> None:
        self.__cdg = convert.ddg.to_cdg(ddg)
        self.__cfg = convert.ddg.to_cfg(ddg)
        self.__ddg = ddg
        self.__pdg = convert.ddg.to_pdg(ddg)
        self.__build_dependencies()

    def init_by_program_dependence_graph(self, pdg: ProgramDependenceGraph) -> None:
        self.__cdg = convert.pdg.to_cdg(pdg)
        self.__cfg = convert.pdg.to_cfg(pdg)
        self.__ddg = convert.pdg.to_ddg(pdg)
        self.__pdg = pdg
        self.__build_dependencies()

    def __build_dependencies(self) -> None:
        self.__main_statements.clear()
        self.__basic_block.clear()
        for block in networkx.algorithms.traversal.dfs_tree(self.__cfg):
            for statement in block:
                self.__basic_block[statement] = block
        self.__scope_dependency = self.__cdg.scope_dependency
        linear_statements = (
            statement
            for statement in self.__cdg if
            statement.statement_type != StatementType.SCOPE and
            statement.statement_type != StatementType.FUNCTION and
            statement.statement_type != StatementType.LOOP and
            statement.statement_type != StatementType.BRANCH and
            statement.statement_type != StatementType.EXIT)
        main_statements = []
        for statement in sorted(linear_statements, key=lambda x: (x.start_point, -x.end_point)):
            if main_statements:
                if statement.start_point >= main_statements[-1].end_point:
                    main_statements.append(statement)
            else:
                main_statements.append(statement)

    def __build_reach_blocks(self, block: BasicBlock, visited_blocks: Set[BasicBlock] = None) -> Set[BasicBlock]:
        if block in self.__reach_blocks:
            return self.__reach_blocks[block]
        if visited_blocks is None:
            visited_blocks = set()
        visited_blocks.add(block)
        result = {block}
        for child in self.__cfg.successors(block):
            if child not in visited_blocks:
                result.update(self.__build_reach_blocks(child, visited_blocks))
        self.__reach_blocks[block] = result
        visited_blocks.remove(block)
        return result

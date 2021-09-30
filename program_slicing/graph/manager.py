__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/23'

from collections import defaultdict
from typing import Dict, Optional, Set, List, Iterable

import networkx

from program_slicing.graph.parse import parse
from program_slicing.graph.cdg import ControlDependenceGraph
from program_slicing.graph.cfg import ControlFlowGraph
from program_slicing.graph.ddg import DataDependenceGraph
from program_slicing.graph.pdg import ProgramDependenceGraph
from program_slicing.graph.point import Point
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
        self.__scope_dependency_backward: Dict[Statement, Set[Statement]] = {}
        self.__function_dependency: Dict[Statement, Statement] = {}
        self.__statement_line_numbers: Dict[Statement, Set[int]] = {}
        self.__general_statements: List[Statement] = []
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

    @property
    def general_statements(self) -> List[Statement]:
        """
        Statement is a 'general' Statement if it is not contained in any
        non SCOPE, BRANCH, LOOP, FUNCTION or EXIT Statement.
        :return: list of general Statements.
        """
        return self.__general_statements

    @property
    def scope_statements(self) -> Iterable[Statement]:
        """
        Statement is a 'scope' Statement if it is SCOPE, BRANCH, LOOP or FUNCTION.
        :return: set of scope Statements.
        """
        return self.__scope_dependency_backward.keys()

    def get_control_dependence_graph(self) -> ControlDependenceGraph:
        return self.__cdg

    def get_control_flow_graph(self) -> ControlFlowGraph:
        return self.__cfg

    def get_data_dependence_graph(self) -> DataDependenceGraph:
        return self.__ddg

    def get_program_dependence_graph(self) -> ProgramDependenceGraph:
        return self.__pdg

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

    def get_statement_line_numbers(self, statement: Statement) -> Set[int]:
        if statement in self.__statement_line_numbers:
            return self.__statement_line_numbers[statement]
        inner_statements = self.get_statements_in_scope(statement)
        if inner_statements:
            result = set()
            if statement.statement_type in {StatementType.SCOPE, StatementType.BRANCH, StatementType.LOOP}:
                result.add(statement.start_point.line_number)
            if statement.statement_type == StatementType.SCOPE:
                result.add(statement.end_point.line_number)
            for inner_statement in inner_statements:
                result.update(self.get_statement_line_numbers(inner_statement))
            self.__statement_line_numbers[statement] = result
        else:
            result = {
                number
                for number in range(statement.start_point.line_number, statement.end_point.line_number + 1)
            }
            self.__statement_line_numbers[statement] = result
        return result

    def get_function_statement(self, statement: Statement) -> Optional[Statement]:
        return self.__function_dependency.get(statement, None)

    def get_function_statement_by_range(self, start_point: Point, end_point: Point) -> Optional[Statement]:
        # TODO: this function may be significantly faster if we will maintain sorted list of Statements.
        statements = sorted(self.get_statements_in_range(start_point, end_point), key=lambda x: x.start_point)
        return self.get_function_statement(statements[0]) if statements else None

    def get_scope_statement(self, statement: Statement) -> Optional[Statement]:
        return self.__scope_dependency.get(statement, None)

    def get_statements_in_scope(self, scope: Statement) -> Set[Statement]:
        return self.__scope_dependency_backward.get(scope, set())

    def get_statements_in_range(
            self,
            start_point: Point = None,
            end_point: Point = None) -> Set[Statement]:
        # TODO: this function may be optimized
        result = set()
        for statement in self.__cdg:
            if (start_point is None or start_point <= statement.start_point) and \
                    (end_point is None or end_point >= statement.end_point):
                result.add(statement)
        return result

    def get_exit_statements(self, statements: Iterable[Statement]) -> Set[Statement]:
        start_point = min(statement.start_point for statement in statements)
        end_point = max(statement.end_point for statement in statements)
        exit_statements = set()
        for statement in statements:
            if statement not in self.__cdg.control_flow:
                continue
            for flow_statement in self.__cdg.control_flow[statement]:
                if flow_statement.start_point < start_point or flow_statement.end_point > end_point:
                    exit_statements.add(flow_statement)
        return exit_statements

    def get_affecting_statements(self, statements: Set[Statement]) -> Set[Statement]:
        assignment_statements = [
            statement for statement in statements
            if
            statement.statement_type == StatementType.ASSIGNMENT or
            statement.statement_type == StatementType.VARIABLE
        ]
        arg_statements_by_arg_name = self.__get_arg_statements_by_arg_name(statements)
        affecting_statements = set()
        for assignment_statement in assignment_statements:
            if assignment_statement not in self.__ddg:
                continue
            for affected_statement in self.__ddg.successors(assignment_statement):
                if affected_statement not in statements or \
                        affected_statement.end_point <= assignment_statement.end_point and \
                        affected_statement in arg_statements_by_arg_name.get(assignment_statement.name, set()):
                    affecting_statements.add(assignment_statement)
                    break
        return affecting_statements

    def get_changed_variables(self, statements: Iterable[Statement]) -> Set[Statement]:
        used_variables = set()
        for statement in statements:
            if statement.statement_type == StatementType.VARIABLE:
                used_variables.add(statement)
            if statement.statement_type == StatementType.ASSIGNMENT:
                if statement not in self.__ddg:
                    continue
                for ancestor in networkx.ancestors(self.__ddg, statement):
                    if ancestor.statement_type == StatementType.VARIABLE and ancestor.name == statement.name:
                        used_variables.add(ancestor)
        return used_variables

    def get_used_variables(self, statements: Iterable[Statement]) -> Set[Statement]:
        used_variables = set()
        ddg = self.get_data_dependence_graph()
        for statement in statements:
            if statement not in ddg:
                continue
            if statement.statement_type == StatementType.VARIABLE:
                used_variables.add(statement)
                continue
            for ancestor in networkx.ancestors(ddg, statement):
                if ancestor.statement_type == StatementType.VARIABLE and ancestor.name == statement.name:
                    used_variables.add(ancestor)
        return used_variables

    def contain_redundant_statements(self, statements: Set[Statement]) -> bool:
        for statement in statements:
            if statement.ast_node_type == "else" or statement.ast_node_type == "catch_clause":
                for predecessor in self.__cdg.predecessors(statement):
                    if predecessor not in statements:
                        return True
            elif statement.ast_node_type == "finally_clause" and self.__is_redundant_finally(statement, statements):
                return True
            elif statement.ast_node_type == "if_statement" and self.__is_redundant_if(statement, statements):
                return True
        return False

    def __build_dependencies(self) -> None:
        self.__statement_line_numbers.clear()
        self.__basic_block.clear()
        for block in networkx.traversal.dfs_tree(self.__cfg):
            for statement in block:
                self.__basic_block[statement] = block
        self.__scope_dependency = self.__cdg.scope_dependency
        self.__scope_dependency_backward = self.__build_statements_in_scope()
        self.__function_dependency = self.__build_function_dependency()
        self.__general_statements = self.__build_general_statements()

    def __build_function_dependency(self) -> Dict[Statement, Statement]:
        function_dependency = {}
        for function_statement in sorted(
                (s for s in self.__cdg if s.statement_type == StatementType.FUNCTION),
                key=lambda x: (x.start_point, -x.end_point)):
            for statement in networkx.traversal.dfs_tree(self.__cdg, function_statement):
                function_dependency[statement] = function_statement
        return function_dependency

    def __build_general_statements(self) -> Set[Statement]:
        result = set()
        for scope in self.scope_statements:
            last_statement = None
            for statement in sorted(self.get_statements_in_scope(scope), key=lambda s: (s.start_point, -s.end_point)):
                if statement.start_point == statement.end_point:
                    continue
                if not last_statement or statement.end_point > last_statement.end_point:
                    last_statement = statement
                    result.add(statement)
        return result

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

    def __build_statements_in_scope(self) -> Dict[Statement, Set[Statement]]:
        statements_in_scope = defaultdict(set)
        cdg = self.get_control_dependence_graph()
        for statement in cdg:
            scope = self.get_scope_statement(statement)
            if scope is None:
                continue
            statements_in_scope[scope].add(statement)
        return statements_in_scope

    def __get_arg_statements_by_arg_name(self, statements: Set[Statement]) -> Dict[str, Set[Statement]]:
        arg_statements_by_arg_name = defaultdict(set)
        for statement in statements:
            if statement in self.__ddg and \
                    statement.statement_type != StatementType.ASSIGNMENT and \
                    statement.statement_type != StatementType.VARIABLE:
                for predecessor in self.__ddg.predecessors(statement):
                    if predecessor not in statements:
                        arg_statements_by_arg_name[predecessor.name].add(statement)
        return arg_statements_by_arg_name

    def __is_redundant_finally(self, statement: Statement, statements: Set[Statement]) -> bool:
        finally_block = self.get_basic_block(statement)
        if finally_block is None:
            return True
        for predecessor_block in self.__cfg.predecessors(finally_block):
            if predecessor_block.statements and predecessor_block.statements[-1] not in statements:
                return True
        return False

    def __is_redundant_if(self, statement: Statement, statements: Set[Statement]) -> bool:
        if statement in self.__cdg.control_flow:
            for successor in self.__cdg.control_flow[statement]:
                if successor.ast_node_type == "else" and successor not in statements:
                    return True
        return False

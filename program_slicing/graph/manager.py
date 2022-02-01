__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/23'

from collections import defaultdict
from typing import Dict, Optional, Set, List, Iterable

import networkx

from program_slicing.graph.parse import parse, Lang
from program_slicing.graph.cdg import ControlDependenceGraph
from program_slicing.graph.cfg import ControlFlowGraph
from program_slicing.graph.ddg import DataDependenceGraph
from program_slicing.graph.pdg import ProgramDependenceGraph
from program_slicing.graph.point import Point
from program_slicing.graph.statement import Statement, StatementType
from program_slicing.graph.basic_block import BasicBlock
from program_slicing.graph import convert


class ProgramGraphsManager:

    def __init__(self, source_code: str = None, lang: Lang = None) -> None:
        self.__cdg: Optional[ControlDependenceGraph] = None
        self.__cfg: Optional[ControlFlowGraph] = None
        self.__ddg: Optional[DataDependenceGraph] = None
        self.__pdg: Optional[ProgramDependenceGraph] = None
        self.__basic_blocks: Optional[Dict[Statement, BasicBlock]] = None
        self.__dom_blocks: Optional[Dict[BasicBlock, Set[BasicBlock]]] = None
        self.__reach_blocks: Optional[Dict[BasicBlock, Set[BasicBlock]]] = None
        self.__scope_dependency: Optional[Dict[Statement, Statement]] = None
        self.__scope_dependency_backward: Optional[Dict[Statement, Set[Statement]]] = None
        self.__function_dependency: Optional[Dict[Statement, Statement]] = None
        self.__statement_line_numbers: Optional[Dict[Statement, Set[int]]] = None
        self.__general_statements: Optional[Set[Statement]] = None
        self.__sorted_statements: Optional[List[Statement]] = None
        if source_code is not None and lang is not None:
            self.__build_cdg = lambda: parse.control_dependence_graph(source_code, lang)
            self.__build_cfg = lambda: convert.cdg.to_cfg(self.control_dependence_graph)
            self.__build_ddg = lambda: convert.cdg.to_ddg(self.control_dependence_graph)
            self.__build_pdg = lambda: convert.cdg.to_pdg(self.control_dependence_graph)
        else:
            self.__build_cdg = lambda: ControlDependenceGraph()
            self.__build_cfg = lambda: ControlFlowGraph()
            self.__build_ddg = lambda: DataDependenceGraph()
            self.__build_pdg = lambda: ProgramDependenceGraph()

    @classmethod
    def from_source_code(cls, source_code: str, lang: Lang) -> 'ProgramGraphsManager':
        """
        Build all the graphs by a given source code string and a language description.
        :param source_code: string with the source code.
        :param lang: the source code Lang.
        :return: Program Graphs Manager.
        """
        return cls(source_code, lang)

    @classmethod
    def from_control_dependence_graph(cls, graph: ControlDependenceGraph) -> 'ProgramGraphsManager':
        """
        Build all the graphs by a given Control Dependence Graph.
        :param graph: Control Dependence Graph.
        :return: Program Graphs Manager.
        """
        result = cls()
        result.__build_cdg = lambda: graph
        result.__build_cfg = lambda: convert.cdg.to_cfg(result.control_dependence_graph)
        result.__build_ddg = lambda: convert.cdg.to_ddg(result.control_dependence_graph)
        result.__build_pdg = lambda: convert.cdg.to_pdg(result.control_dependence_graph)
        return result

    @classmethod
    def from_control_flow_graph(cls, graph: ControlFlowGraph) -> 'ProgramGraphsManager':
        """
        Build all the graphs by a given Control Flow Graph.
        :param graph: Control Flow Graph.
        :return: Program Graphs Manager.
        """
        result = cls()
        result.__build_cdg = lambda: convert.cfg.to_cdg(result.control_flow_graph)
        result.__build_cfg = lambda: graph
        result.__build_ddg = lambda: convert.cfg.to_ddg(result.control_flow_graph)
        result.__build_pdg = lambda: convert.cfg.to_pdg(result.control_flow_graph)
        return result

    @classmethod
    def from_data_dependence_graph(cls, graph: DataDependenceGraph) -> 'ProgramGraphsManager':
        """
        Build all the graphs by a given Data Dependence Graph.
        :param graph: Data Dependence Graph.
        :return: Program Graphs Manager.
        """
        result = cls()
        result.__build_cdg = lambda: convert.ddg.to_cdg(result.data_dependence_graph)
        result.__build_cfg = lambda: convert.ddg.to_cfg(result.data_dependence_graph)
        result.__build_ddg = lambda: graph
        result.__build_pdg = lambda: convert.ddg.to_pdg(result.data_dependence_graph)
        return result

    @classmethod
    def from_program_dependence_graph(cls, graph: ProgramDependenceGraph) -> 'ProgramGraphsManager':
        """
        Build all the graphs by a given Program Dependence Graph.
        :param graph: Program Dependence Graph.
        :return: Program Graphs Manager.
        """
        result = cls()
        result.__build_cdg = lambda: convert.pdg.to_cdg(result.program_dependence_graph)
        result.__build_cfg = lambda: convert.pdg.to_cfg(result.program_dependence_graph)
        result.__build_ddg = lambda: convert.pdg.to_ddg(result.program_dependence_graph)
        result.__build_pdg = lambda: graph
        return result

    @property
    def control_dependence_graph(self) -> ControlDependenceGraph:
        """
        Structure that represents Control Dependence Graph (inherited from networkx.DiGraph) with corresponding methods.
        :return: Control Dependence Graph.
        """
        if self.__cdg is None:
            self.__cdg = self.__build_cdg()
        return self.__cdg

    @property
    def control_flow_graph(self) -> ControlFlowGraph:
        """
        Structure that represents Control Flow Graph (inherited from networkx.DiGraph) with corresponding methods.
        :return: Control Flow Graph.
        """
        if self.__cfg is None:
            self.__cfg = self.__build_cfg()
        return self.__cfg

    @property
    def data_dependence_graph(self) -> DataDependenceGraph:
        """
        Structure that represents Data Dependence Graph (inherited from networkx.DiGraph) with corresponding methods.
        :return: Data Dependence Graph.
        """
        if self.__ddg is None:
            self.__ddg = self.__build_ddg()
        return self.__ddg

    @property
    def program_dependence_graph(self) -> ProgramDependenceGraph:
        """
        Structure that represents Program Dependence Graph (inherited from networkx.DiGraph) with corresponding methods.
        :return: Program Dependence Graph.
        """
        if self.__pdg is None:
            self.__pdg = self.__build_pdg()
        return self.__pdg

    @property
    def sorted_statements(self) -> List[Statement]:
        """
        Statements are sorted first increasing of their start_point, then by decreasing of their end_point.
        :return: sorted list of all Statements.
        """
        if self.__sorted_statements is None:
            self.__sorted_statements = self.__build_sorted_statements()
        return self.__sorted_statements

    @property
    def general_statements(self) -> Set[Statement]:
        """
        Statement is 'general' if it is not contained in any non SCOPE, BRANCH, LOOP, FUNCTION or EXIT Statement.
        :return: set of general Statements.
        """
        if self.__general_statements is None:
            self.__general_statements = self.__build_general_statements()
        return self.__general_statements

    @property
    def scope_statements(self) -> Iterable[Statement]:
        """
        Statement is a 'scope' Statement if it is SCOPE, BRANCH, LOOP or FUNCTION.
        :return: set of scope Statements.
        """
        if self.__scope_dependency_backward is None:
            self.__scope_dependency_backward = self.__build_statements_in_scope()
        return self.__scope_dependency_backward.keys()

    def get_basic_block(self, statement: Statement) -> Optional[BasicBlock]:
        """
        Basic Block - structure that represents Control Flow Graph nodes.
        :return: Basic Block that contains the given Statement.
        """
        if self.__basic_blocks is None:
            self.__basic_blocks = self.__build_basic_blocks()
        return self.__basic_blocks.get(statement, None)

    def get_boundary_blocks(self, block: BasicBlock) -> Set[BasicBlock]:
        """
        Get a set of Basic Blocks which intersection of dominated and reach blocks contain the given one block.
        :param block: Basic Block for which the boundary blocks should to be obtained.
        :return: set of boundary Basic Blocks.
        """
        boundary_blocks = set()
        for basic_block in self.control_flow_graph:
            if block in self.get_dominated_blocks(basic_block).intersection(self.get_reach_blocks(basic_block)):
                boundary_blocks.add(basic_block)
        return boundary_blocks

    def get_boundary_blocks_for_statement(self, statement: Statement) -> Set[BasicBlock]:
        """
        Get a set of boundary blocks for BasicBlock in which the given Statement is placed.
        :param statement: Statement for which the boundary blocks should to be obtained.
        :return: set of boundary Basic Blocks.
        """
        block = self.get_basic_block(statement)
        return self.get_boundary_blocks(block)

    def get_dominated_blocks(self, block: BasicBlock) -> Set[BasicBlock]:
        """
        Get a set of Basic Blocks which are reachable in Control Dependence Graph from the parent of the given block.
        :param block: Basic Block for which the dominated blocks should to be obtained.
        :return: set of dominated Basic Blocks.
        """
        if self.__dom_blocks is None:
            self.__dom_blocks = {}
        if block in self.__dom_blocks:
            return self.__dom_blocks[block]
        result = {block}
        root = block.root
        if root is None:
            return result
        predecessors = [predecessor for predecessor in self.control_dependence_graph.predecessors(root)]
        if len(predecessors) == 0:
            predecessors = [root]
        for root in predecessors:
            for statement in networkx.algorithms.bfs_tree(self.control_dependence_graph, root):
                if statement == root:
                    continue
                current_block = self.get_basic_block(statement)
                if current_block is not None:
                    result.add(current_block)
        self.__dom_blocks[block] = result
        return result

    def get_reach_blocks(self, block: BasicBlock) -> Set[BasicBlock]:
        """
        Get a set of Basic Blocks which are reachable in Control Flow Graph from the the given block (including itself).
        :param block: Basic Block for which the reach blocks should to be obtained.
        :return: set of reach Basic Blocks.
        """
        if self.__reach_blocks is None:
            self.__reach_blocks = {}
        return self.__build_reach_blocks(block)

    def get_statement_line_numbers(self, statement: Statement) -> Set[int]:
        """
        Get a set of line numbers in which the given Statement is placed.
        :param statement: Statement for which the line numbers should to be obtained.
        :return: set of line numbers (integers).
        """
        if self.__statement_line_numbers is None:
            self.__statement_line_numbers = {}
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
        """
        Get the minimal FUNCTION Statement in which the given Statement is placed.
        :param statement: Statement for which the FUNCTION statement should to be obtained.
        :return: FUNCTION Statement or None if not found.
        """
        if self.__function_dependency is None:
            self.__function_dependency = self.__build_function_dependency()
        return self.__function_dependency.get(statement, None)

    def get_function_statement_by_range(self, start_point: Point, end_point: Point) -> Optional[Statement]:
        """
        Get the minimal FUNCTION Statement in which the given range is placed.
        :param start_point: start Point of the given range.
        :param end_point: end Point of the given range.
        :return: FUNCTION Statement or None if not found.
        """
        statements = self.sorted_statements
        start_statement_idx = self.__bisect_range_left(start_point, end_point)
        if start_statement_idx >= len(statements):
            return None
        return self.get_function_statement(statements[start_statement_idx])

    def get_scope_statement(self, statement: Statement) -> Optional[Statement]:
        """
        Get the minimal SCOPE, BRANCH, LOOP or FUNCTION Statement in which the given Statement is placed.
        :param statement: Statement for which the scope statement should to be obtained.
        :return: SCOPE, BRANCH, LOOP or FUNCTION Statement (or None if not found).
        """
        if self.__scope_dependency is None:
            self.__scope_dependency = self.control_dependence_graph.scope_dependency
        return self.__scope_dependency.get(statement, None)

    def get_statements_in_scope(self, scope: Statement) -> Set[Statement]:
        """
        Get all the Statements in the given scope Statement.
        :param scope: Statement for which contained Statements should to be obtained.
        :return: set of Statements contained in the given Statement,
        set will be empty if the given Statement is not SCOPE, BRANCH, LOOP or FUNCTION.
        """
        if self.__scope_dependency_backward is None:
            self.__scope_dependency_backward = self.__build_statements_in_scope()
        return self.__scope_dependency_backward.get(scope, set())

    def get_statements_in_range(self, start_point: Point = None, end_point: Point = None) -> Set[Statement]:
        """
        Get all the Statements in the given range.
        :param start_point: start Point of the given range.
        :param end_point: end Point of the given range.
        :return: set of Statements contained in the given range.
        """
        statements = self.sorted_statements
        start_statement_idx = 0 if start_point is None else self.__bisect_range_left(start_point, end_point)
        end_statement_idx = len(statements) if end_point is None else self.__bisect_range_right(end_point, end_point)
        return set(
            statements[idx]
            for idx in range(start_statement_idx, end_statement_idx)
            if (start_point is None or start_point <= statements[idx].start_point) and
            (end_point is None or end_point >= statements[idx].end_point)
        )

    def get_exit_statements(self, statements: Set[Statement]) -> Set[Statement]:
        """
        Get Statements that are Flow Dependence children of the given statements but not one of them.
        :param statements: set of Statements for which exit Statements should to be obtained.
        :return: set of exit Statements (may have not only EXIT type).
        """
        start_point = min(statement.start_point for statement in statements)
        end_point = max(statement.end_point for statement in statements)
        exit_statements = set()
        flow_statements = set()
        for statement in statements:
            if statement not in self.control_dependence_graph.control_flow:
                continue
            flow_statements.update(self.control_dependence_graph.control_flow[statement])
        visited = set()
        while flow_statements:
            level = set()
            for flow_statement in flow_statements:
                if flow_statement in statements:
                    continue
                if flow_statement.start_point < start_point or flow_statement.end_point > end_point:
                    exit_statements.add(flow_statement)
                elif flow_statement.statement_type == StatementType.EXIT:
                    exit_statements.add(flow_statement)
                elif flow_statement not in visited and flow_statement in self.control_dependence_graph.control_flow:
                    level.update(self.control_dependence_graph.control_flow[flow_statement])
                    visited.add(flow_statement)
            flow_statements = level
        return exit_statements

    def get_affecting_statements(self, statements: Set[Statement]) -> Set[Statement]:
        """
        Get Statements from the given set that affect by Data Dependence some Statement not form the given set.
        :param statements: set of Statements for which affecting Statements should to be obtained.
        :return: set of affecting Statements (may have VARIABLE, OBJECT or ASSIGNMENT type).
        """
        assignment_statements = [
            statement for statement in statements
            if statement.statement_type in {
                StatementType.ASSIGNMENT,
                StatementType.VARIABLE,
                StatementType.OBJECT
            }
        ]
        arg_statements_by_arg_name = self.__get_arg_statements_by_arg_name(statements)
        ddg = self.data_dependence_graph
        affecting_statements = set()
        for assignment_statement in assignment_statements:
            if assignment_statement not in ddg:
                continue
            for affected_statement in networkx.descendants(ddg, assignment_statement):
                if affected_statement.statement_type in {StatementType.VARIABLE, StatementType.OBJECT}:
                    if affected_statement.name != assignment_statement.name and \
                            assignment_statement.name not in affected_statement.affected_by:
                        continue
                elif assignment_statement.name not in affected_statement.affected_by:
                    continue
                if affected_statement not in statements or \
                        affected_statement.end_point <= assignment_statement.end_point and \
                        affected_statement in arg_statements_by_arg_name.get(assignment_statement.name, set()):
                    affecting_statements.add(assignment_statement)
                    break
        return affecting_statements

    def get_changed_variables_statements(self, statements: Iterable[Statement]) -> Set[Statement]:
        """
        Get VARIABLE and OBJECT Statements that represent variables changed in the given set of Statements.
        :param statements: set of Statements for which changed variables should to be obtained.
        :return: set of changed variables (Statements with VARIABLE or OBJECT type).
        """
        changed_variables = set()
        ddg = self.data_dependence_graph
        for statement in statements:
            if statement not in ddg:
                continue
            if statement.statement_type in {StatementType.VARIABLE, StatementType.OBJECT}:
                changed_variables.add(statement)
            elif statement.statement_type == StatementType.ASSIGNMENT:
                if statement not in ddg:
                    continue
                for ancestor in networkx.ancestors(ddg, statement):
                    if ancestor.statement_type in {StatementType.VARIABLE, StatementType.OBJECT} \
                            and ancestor.name == statement.name:
                        changed_variables.add(ancestor)
                        break
        return changed_variables

    def get_involved_variables_statements(self, statements: Iterable[Statement]) -> Set[Statement]:
        """
        Get VARIABLE and OBJECT Statements that represent variables involved (including usage) in the given Statements.
        :param statements: set of Statements for which involved variables should to be obtained.
        :return: set of involved variables (Statements with VARIABLE or OBJECT type).
        """
        involved_variables = set()
        ddg = self.data_dependence_graph
        for statement in statements:
            if statement not in ddg:
                continue
            if statement.statement_type in {StatementType.VARIABLE, StatementType.OBJECT}:
                involved_variables.add(statement)
            for ancestor in networkx.ancestors(ddg, statement):
                if ancestor.statement_type in {StatementType.VARIABLE, StatementType.OBJECT} \
                        and ancestor.name in statement.affected_by:
                    involved_variables.add(ancestor)
        return involved_variables

    def __build_basic_blocks(self) -> Dict[Statement, BasicBlock]:
        basic_blocks = {}
        for block in networkx.traversal.dfs_tree(self.control_flow_graph):
            for statement in block:
                basic_blocks[statement] = block
        return basic_blocks

    def __build_function_dependency(self) -> Dict[Statement, Statement]:
        function_dependency = {}
        for function_statement in sorted(
                (s for s in self.control_dependence_graph if s.statement_type == StatementType.FUNCTION),
                key=lambda x: (x.start_point, -x.end_point)):
            for statement in networkx.traversal.dfs_tree(self.control_dependence_graph, function_statement):
                function_dependency[statement] = function_statement
        return function_dependency

    def __build_sorted_statements(self) -> List[Statement]:
        return sorted(self.control_dependence_graph, key=lambda s: (s.start_point, -s.end_point))

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
        for child in self.control_flow_graph.successors(block):
            if child not in visited_blocks:
                result.update(self.__build_reach_blocks(child, visited_blocks))
        self.__reach_blocks[block] = result
        visited_blocks.remove(block)
        return result

    def __build_statements_in_scope(self) -> Dict[Statement, Set[Statement]]:
        statements_in_scope = defaultdict(set)
        for statement in self.control_dependence_graph:
            scope = self.get_scope_statement(statement)
            if scope is None:
                continue
            statements_in_scope[scope].add(statement)
        return statements_in_scope

    def __get_arg_statements_by_arg_name(self, statements: Set[Statement]) -> Dict[str, Set[Statement]]:
        arg_statements_by_arg_name = defaultdict(set)
        for statement in statements:
            if statement in self.data_dependence_graph and statement.statement_type not in {
                StatementType.VARIABLE,
                StatementType.OBJECT,
                StatementType.ASSIGNMENT
            }:
                for predecessor in self.data_dependence_graph.predecessors(statement):
                    if predecessor not in statements:
                        if predecessor.statement_type in {StatementType.VARIABLE, StatementType.OBJECT}:
                            arg_statements_by_arg_name[predecessor.name].add(statement)
                        else:
                            for predecessor_name in statement.affected_by.intersection(predecessor.affected_by):
                                arg_statements_by_arg_name[predecessor_name].add(statement)
        return arg_statements_by_arg_name

    def __bisect_range_left(self, start_point: Point, end_point: Point) -> int:
        searching_range = (start_point, -end_point)
        a = self.sorted_statements
        lo = 0
        hi = len(a)
        while lo < hi:
            mid = (lo + hi) // 2
            if (a[mid].start_point, -a[mid].end_point) < searching_range:
                lo = mid + 1
            else:
                hi = mid
        return lo

    def __bisect_range_right(self, start_point: Point, end_point: Point) -> int:
        searching_range = (start_point, -end_point)
        a = self.sorted_statements
        lo = 0
        hi = len(a)
        while lo < hi:
            mid = (lo + hi) // 2
            if searching_range < (a[mid].start_point, -a[mid].end_point):
                hi = mid
            else:
                lo = mid + 1
        return lo

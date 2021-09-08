__licence__ = 'MIT'
__author__ = 'lyriccoder'
__credits__ = ['lyriccoder, kuyaki']
__maintainer__ = 'lyriccoder'
__date__ = '2021/05/20'

from collections import defaultdict
from itertools import combinations_with_replacement
from typing import Iterable, Set, Dict

import networkx

from program_slicing.decomposition.program_slice import ProgramSlice
from program_slicing.decomposition.slice_predicate import SlicePredicate
from program_slicing.graph.cdg import ControlDependenceGraph
from program_slicing.graph.cfg import ControlFlowGraph
from program_slicing.graph.ddg import DataDependenceGraph
from program_slicing.graph.manager import ProgramGraphsManager
from program_slicing.graph.statement import StatementType, Statement
from program_slicing.graph.parse import control_dependence_graph, control_flow_graph
from program_slicing.graph.parse import data_dependence_graph, LANG_JAVA


def __build_function_dependency(self):
    function_dependency = {}
    for function_statement in sorted(
            (s for s in self.__cdg if s.statement_type == StatementType.FUNCTION),
            key=lambda x: (x.start_point, -x.end_point)):
        for statement in networkx.traversal.dfs_tree(self.__cdg, function_statement):
            function_dependency[statement] = function_statement
    return function_dependency


def build_statements_in_scope(cdg):
    statements_in_scope = defaultdict(set)
    for statement in cdg:
        scope = cdg.scope_dependency.get(statement, None)
        if scope is not None:
            statements_in_scope[scope].add(statement)

    return statements_in_scope


def build_function_dependency(cdg):
    function_dependency = {}
    for function_statement in sorted(
            (s for s in cdg if s.statement_type == StatementType.FUNCTION),
            key=lambda x: (x.start_point, -x.end_point)):
        for statement in networkx.traversal.dfs_tree(cdg, function_statement):
            function_dependency[statement] = function_statement
    return function_dependency


def get_arg_statements_by_arg_name(statements: Set[Statement], ddg) -> Dict[str, Set[Statement]]:
    arg_statements_by_arg_name = defaultdict(set)
    for statement in statements:
        if statement in ddg and \
                statement.statement_type not in [StatementType.ASSIGNMENT, StatementType.VARIABLE]:
            for predecessor in ddg.predecessors(statement):
                if predecessor not in statements:
                    arg_statements_by_arg_name[predecessor.name].add(statement)
    return arg_statements_by_arg_name


def get_affecting_statements(statements: Set[Statement], ddg) -> Set[Statement]:
    assignment_statements = [
        statement for statement in statements
        if statement.statement_type in [StatementType.ASSIGNMENT, StatementType.VARIABLE] and statement in ddg
    ]
    arg_statements_by_arg_name = get_arg_statements_by_arg_name(statements, ddg)
    affecting_statements = set()
    # Can we optimize it? WHAT IS IT
    for assignment_statement in assignment_statements:
        for affected_statement in ddg.successors(assignment_statement):
            if affected_statement not in statements or \
                    affected_statement.end_point <= assignment_statement.end_point and \
                    affected_statement in arg_statements_by_arg_name.get(assignment_statement.name, set()):
                affecting_statements.add(assignment_statement)
                break
    return affecting_statements


def get_used_variables(ddg, statements: Iterable[Statement]) -> Set[Statement]:
    used_variables = set()
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


def is_redundant_finally(statement: Statement, statements: Set[Statement], cfg, basic_block) -> bool:
    finally_block = basic_block.get(statement, None)
    if finally_block is None:
        return True
    for predecessor_block in cfg.predecessors(finally_block):
        if predecessor_block.statements and predecessor_block.statements[-1] not in statements:
            return True
    return False


def is_redundant_if(statement: Statement, statements: Set[Statement], cdg) -> bool:
    if statement in cdg.control_flow:
        for successor in cdg.control_flow[statement]:
            if successor.ast_node_type == "else" and successor not in statements:
                return True
    return False


def contain_redundant_statements(statements: Set[Statement], cdg, cfg, basic_block) -> bool:
    for statement in statements:
        if statement.ast_node_type in ["else", "catch_clause"]:
            for predecessor in cdg.predecessors(statement):
                if predecessor not in statements:
                    return True
        elif statement.ast_node_type == "finally_clause" \
                and is_redundant_finally(statement, statements, cfg, basic_block):
            return True
        elif statement.ast_node_type == "if_statement" and is_redundant_if(statement, statements, cdg):
            return True
    return False

def build_general_statements(scopes) -> Set[Statement]:
    result = set()
    for scope in scopes:
        last_statement = None
        for statement in sorted(get_statements_in_scope(scopes, scope), key=lambda s: (s.start_point, -s.end_point)):
            if statement.start_point == statement.end_point:
                continue
            if not last_statement or statement.end_point > last_statement.end_point:
                last_statement = statement
                result.add(statement)
    return result


def get_statements_in_scope(scopes, scope) -> Set[Statement]:
    return scopes.get(scope, set())


def get_exit_statements(statements: Iterable[Statement], cdg) -> Set[Statement]:
    start_point = min(statement.start_point for statement in statements)
    end_point = max(statement.end_point for statement in statements)
    exit_statements = set()
    for statement in statements:
        if statement not in cdg.control_flow:
            continue
        for flow_statement in cdg.control_flow[statement]:
            if flow_statement.start_point < start_point or flow_statement.end_point > end_point:
                exit_statements.add(flow_statement)
    return exit_statements


def get_block_slices(
        source_code: str,
        lang: str,
        slice_predicate: SlicePredicate = None,
        max_percentage_of_lines: float = None,
        may_cause_code_duplication: bool = False) -> Iterable[ProgramSlice]:
    """
    For each a specified source code generate list of Program Slices based on continues blocks.
    :param source_code: source code that should be decomposed.
    :param lang: string with the source code format described as a file ext (like '.java' or '.xml').
    :param slice_predicate: SlicePredicate object that describes which slices should be filtered. No filtering if None.
    :param max_percentage_of_lines: number of lines in each slice shouldn't exceed a corresponding
    share of source lines specified by float number [0.0, 1.0].
    :param may_cause_code_duplication: allow to generate slices which extraction will cause code duplication if True.
    :return: generator of the ProgramSlices.
    """
    source_lines = source_code.split("\n")
    manager = ProgramGraphsManager(source_code, lang)
    cdg: ControlDependenceGraph = control_dependence_graph(source_code, lang)
    ddg: DataDependenceGraph = data_dependence_graph(source_code, LANG_JAVA)
    cfg: ControlFlowGraph = control_flow_graph(source_code, LANG_JAVA)
    basic_block = {}
    for block in networkx.traversal.dfs_tree(cfg):
        for statement in block:
            basic_block[statement] = block

    scopes = build_statements_in_scope(cdg)
    function_dependency = build_function_dependency(cdg)
    # manager_scopes = manager.scope_statements
    # manager_scopes_set = set(
    #     [tuple([x.statement_type.name, x.start_point, x.end_point, x.ast_node_type])
    #      for x in manager_scopes])
    # manager_scope = set(
    #     [tuple([x.statement_type.name, x.start_point, x.end_point, x.ast_node_type])
    #      for x in scopes.keys()])

    # print(set(manager_scopes_set).difference(set(manager_scope)), '#####################################')
    # print()
    for scope in scopes:
        function_statement = function_dependency.get(scope, None)
        if function_statement is None:
            continue
        function_length = function_statement.end_point.line_number - function_statement.start_point.line_number + 1
        all_statement_in_scope = sorted(
            get_statements_in_scope(scopes, scope), key=lambda s: (s.start_point, -s.end_point))
        non_filtered_general_statements = build_general_statements(scopes)
        general_statements = sorted((
            statement
            for statement in all_statement_in_scope
            if statement in non_filtered_general_statements),
            key=lambda x: (x.start_point, -x.end_point))
        # general_statements = sorted((
        #     statement
        #     for statement in all_statement_in_scope
        #     if statement in build_general_statements(scopes, all_statement_in_scope),
        #     key=lambda x: (x.start_point, -x.end_point))
        id_combinations = [
            c for c in combinations_with_replacement([idx for idx in range(len(general_statements))], 2)
        ]
        for ids in id_combinations:
            current_statements = general_statements[ids[0]: ids[1] + 1]
            if not current_statements:
                continue
            if max_percentage_of_lines is not None and __percentage_or_amount_exceeded(
                    function_length,
                    current_statements[-1].end_point.line_number - current_statements[0].start_point.line_number + 1,
                    max_percentage_of_lines):
                continue
            extended_statements = manager.get_statements_in_range(
                current_statements[0].start_point,
                current_statements[-1].end_point)
            if not may_cause_code_duplication:
                affecting_statements = get_affecting_statements(extended_statements, ddg)
                if len(get_used_variables(affecting_statements, ddg)) > 1 or \
                        contain_redundant_statements(extended_statements, cdg, cfg, basic_block):
                        # manager.contain_redundant_statements(extended_statements, cdg, cfg):
                    continue
            if len(get_exit_statements(extended_statements, cdg)) > 1:
                continue
            program_slice = ProgramSlice(source_lines).from_statements(extended_statements)
            if slice_predicate is None or slice_predicate(program_slice, scopes=scopes):
                yield program_slice


def __percentage_or_amount_exceeded(outer_number, inner_number, percentage):
    #  (outer_number - 3) is number of lines in regular function body
    #  so that we also check that not all the lines from body are included.
    return float(inner_number) / outer_number > percentage or inner_number > outer_number - 4

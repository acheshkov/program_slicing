__licence__ = 'MIT'
__author__ = 'lyriccoder'
__credits__ = ['lyriccoder, kuyaki']
__maintainer__ = 'lyriccoder'
__date__ = '2021/05/20'

from collections import defaultdict
from itertools import combinations_with_replacement
from typing import Iterable, List, Dict, Set

import networkx

from program_slicing.decomposition.program_slice import ProgramSlice
from program_slicing.decomposition.slice_predicate import SlicePredicate
from program_slicing.graph.manager import ProgramGraphsManager
from program_slicing.graph.statement import Statement, StatementType
from program_slicing.graph.point import Point


def build_opportunities_filtered(
        source_code: str,
        lang: str,
        min_amount_of_lines: int = None,
        max_amount_of_lines: int = None,
        max_percentage_of_lines: float = None) -> Iterable[ProgramSlice]:
    slice_predicate = SlicePredicate(
        min_amount_of_lines=min_amount_of_lines,
        max_amount_of_lines=max_amount_of_lines,
        lines_are_full=True,
        lang_to_check_parsing=lang)
    return (program_slice for program_slice in build_opportunities(
        source_code,
        lang,
        max_percentage_of_lines=max_percentage_of_lines
    ) if slice_predicate(program_slice))


def build_opportunities(source_code: str, lang: str, max_percentage_of_lines=None) -> Iterable[ProgramSlice]:
    source_lines = source_code.split("\n")
    manager = ProgramGraphsManager(source_code, lang)
    control_flow_dict = manager.get_control_dependence_graph().control_flow
    statements_in_scope = __build_statements_in_scope(manager)
    for scope, statements in statements_in_scope.items():
        dominant_statements = __build_dominant_statements(statements)
        id_combinations = [
            c for c in combinations_with_replacement([idx for idx in range(len(dominant_statements))], 2)
        ]
        for ids in id_combinations:
            current_statements = dominant_statements[ids[0]: ids[1] + 1]
            elder_statements = {
                s for s in manager.get_control_dependence_graph()
                if s.start_point >= current_statements[-1].end_point
            }
            if not current_statements:
                continue
            if max_percentage_of_lines is not None:
                lines_n = \
                    current_statements[-1].end_point.line_number - current_statements[0].start_point.line_number + 1
                if float(lines_n) / len(source_lines) > max_percentage_of_lines:
                    continue
            extended_statements = __get_all_statements(
                manager,
                current_statements[0].start_point,
                current_statements[-1].end_point)
            changed_variables = __get_changed_variables(manager, extended_statements)
            used_variables = __get_used_variables(manager, elder_statements)
            changed_and_used_variables = changed_variables.intersection(used_variables)
            if len(changed_and_used_variables) > 1:
                continue
            if len(__get_outer_goto(manager, extended_statements, scope)) > 0:
                continue
            if __contain_redundant_statements(manager, extended_statements):
                continue
            exit_statements = set()
            for statement in extended_statements:
                if statement not in control_flow_dict:
                    continue
                for flow_statement in control_flow_dict[statement]:
                    if flow_statement in elder_statements:
                        exit_statements.add(flow_statement)
            if len(exit_statements) > 1:
                continue
            yield ProgramSlice(source_lines).from_statements(extended_statements)


def __build_statements_in_scope(manager: ProgramGraphsManager) -> Dict[Statement, Set[Statement]]:
    statements_in_scope = defaultdict(set)
    cdg = manager.get_control_dependence_graph()
    for statement in cdg:
        scope = manager.get_scope_statement(statement)
        if scope is None:
            continue
        statements_in_scope[scope].add(statement)
    return statements_in_scope


def __build_dominant_statements(statements: Iterable[Statement]) -> List[Statement]:
    statements = sorted(
        statements,
        key=lambda s: (s.start_point, (-s.end_point.line_number, -s.end_point.column_number)))
    result = []
    for statement in statements:
        if not result or statement.end_point > result[-1].end_point:
            result.append(statement)
    return result


def __get_all_statements(
        manager: ProgramGraphsManager,
        start_point: Point = None,
        end_point: Point = None) -> Set[Statement]:
    result = set()
    for statement in manager.get_control_dependence_graph():
        if (start_point is None or start_point <= statement.start_point) and \
                (end_point is None or end_point >= statement.end_point):
            result.add(statement)
    return result


def __get_changed_variables(manager: ProgramGraphsManager, statements: Iterable[Statement]) -> Set[Statement]:
    used_variables = set()
    for statement in statements:
        if statement.statement_type == StatementType.VARIABLE:
            used_variables.add(statement)
        if statement.statement_type == StatementType.ASSIGNMENT:
            if statement not in manager.get_data_dependence_graph():
                continue
            for ancestor in networkx.ancestors(manager.get_data_dependence_graph(), statement):
                if ancestor.statement_type == StatementType.VARIABLE and ancestor.name == statement.name:
                    used_variables.add(ancestor)
    return used_variables


def __get_used_variables(manager: ProgramGraphsManager, statements: Iterable[Statement]) -> Set[Statement]:
    used_variables = set()
    for statement in statements:
        if statement not in manager.get_data_dependence_graph():
            continue
        for ancestor in networkx.ancestors(manager.get_data_dependence_graph(), statement):
            if ancestor.statement_type == StatementType.VARIABLE and ancestor.name == statement.name:
                used_variables.add(ancestor)
    return used_variables


def __get_outer_goto(
        manager: ProgramGraphsManager,
        statements: Iterable[Statement],
        scope: Statement) -> Set[Statement]:
    cdg = manager.get_control_dependence_graph()
    scope = 0 if scope is None else scope
    outer_goto = set()
    for statement in statements:
        if statement.statement_type == StatementType.GOTO:
            if statement in cdg.control_flow:
                for flow_statement in cdg[statement]:
                    if flow_statement.start_point < scope.start_point or flow_statement.end_point > scope.end_point:
                        outer_goto.add(statement)
    return outer_goto


def __contain_redundant_statements(manager: ProgramGraphsManager, statements: Set[Statement]) -> bool:
    for statement in statements:
        if statement.ast_node_type == "else" or statement.ast_node_type == "catch_clause":
            for predecessor in manager.get_control_dependence_graph().predecessors(statement):
                if predecessor not in statements:
                    return True
        elif statement.ast_node_type == "finally_clause" and __is_redundant_finally(manager, statement, statements):
            return True
        elif statement.ast_node_type == "if_statement" and __is_redundant_if(manager, statement, statements):
            return True
    return False


def __is_redundant_finally(manager: ProgramGraphsManager, statement: Statement, statements: Set[Statement]) -> bool:
    cfg = manager.get_control_flow_graph()
    finally_block = manager.get_basic_block(statement)
    if finally_block is None:
        return True
    for predecessor_block in cfg.predecessors(finally_block):
        if predecessor_block.statements and predecessor_block.statements[-1] not in statements:
            return True
    return False


def __is_redundant_if(manager: ProgramGraphsManager, statement: Statement, statements: Set[Statement]) -> bool:
    cdg = manager.get_control_dependence_graph()
    if statement in cdg.control_flow:
        for successor in cdg.control_flow[statement]:
            if successor.ast_node_type == "else" and successor not in statements:
                return True
    return False

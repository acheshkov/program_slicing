__licence__ = 'MIT'
__author__ = 'lyriccoder'
__credits__ = ['lyriccoder, kuyaki']
__maintainer__ = 'lyriccoder'
__date__ = '2021/05/20'

from itertools import combinations_with_replacement
from typing import Iterable, List, Tuple

from program_slicing.decomposition.program_slice import ProgramSlice
from program_slicing.decomposition.slice_predicate import SlicePredicate
from program_slicing.graph.manager import ProgramGraphsManager
from program_slicing.graph.statement import Statement, StatementType


def get_block_slices(
        source_code: str,
        lang: str,
        slice_predicate: SlicePredicate = None,
        include_noneffective: bool = True,
        may_cause_code_duplication: bool = False,
        unite_statements_into_groups: bool = False) -> Iterable[ProgramSlice]:
    """
    For each a specified source code generate list of Program Slices based on continues blocks.
    :param source_code: source code that should be decomposed.
    :param lang: string with the source code format described as a file ext (like '.java' or '.xml').
    :param slice_predicate: SlicePredicate object that describes which slices should be filtered. No filtering if None.
    :param include_noneffective: include comments and blank lines to a slice if True.
    :param may_cause_code_duplication: allow to generate slices which extraction will cause code duplication if True.
    :param unite_statements_into_groups: will unite function calls, assignment and declarations into groups if True.
    :return: generator of the ProgramSlices.
    """
    source_lines = source_code.split("\n")
    manager = ProgramGraphsManager(source_code, lang)
    for scope in manager.scope_statements:
        function_statement = manager.get_function_statement(scope)
        if function_statement is None:
            continue
        statements_in_scope = manager.get_statements_in_scope(scope)
        general_statements = sorted((
            statement
            for statement in statements_in_scope
            if statement in manager.general_statements),
            key=lambda x: (x.start_point, -x.end_point))
        general_groups = __build_general_groups(general_statements) if unite_statements_into_groups else [
            [statement] for statement in general_statements
        ]
        id_combinations = (
            c for c in combinations_with_replacement([idx for idx in range(len(general_groups))], 2)
            if __pre_check(general_groups, c, slice_predicate, source_lines)
        )
        for ids in id_combinations:
            current_groups = general_groups[ids[0]: ids[1] + 1]
            if not current_groups:
                continue
            extended_statements = manager.get_statements_in_range(
                current_groups[0][0].start_point,
                current_groups[-1][-1].end_point)
            if not may_cause_code_duplication:
                affecting_statements = manager.get_affecting_statements(extended_statements)
                if len(manager.get_involved_variables(affecting_statements)) > 1 or \
                        manager.contain_redundant_statements(extended_statements):
                    continue
            if len(manager.get_exit_statements(extended_statements)) > 1:
                continue
            program_slice = ProgramSlice(
                source_lines,
                context=manager if include_noneffective else None
            ).from_statements(extended_statements)
            if slice_predicate is None or slice_predicate(program_slice, context=manager):
                yield program_slice


def __pre_check(
        groups: List[List[Statement]],
        ids: Tuple[int, ...],
        slice_predicate: SlicePredicate,
        source_lines: List[str]) -> bool:
    if slice_predicate:
        if slice_predicate.min_amount_of_lines is not None:
            max_lines_number = \
                groups[ids[1]][-1].end_point.line_number - groups[ids[0]][0].start_point.line_number + 1
            if max_lines_number < slice_predicate.min_amount_of_lines:
                return False
        if slice_predicate.max_amount_of_statements is not None:
            min_statements_number = sum(len(groups[i]) for i in range(ids[0], ids[1] + 1))
            if min_statements_number > slice_predicate.max_amount_of_statements:
                return False
        if slice_predicate.lines_are_full is not None:
            noneffective = {' ', '\t', '\n', '\r'}
            line_n = groups[ids[0]][0].start_point.line_number
            column_n = groups[ids[0]][0].start_point.column_number
            start_line_part = source_lines[line_n][:column_n]
            if "//" not in start_line_part and any(c not in noneffective for c in start_line_part):
                return not slice_predicate.lines_are_full
            line_n = groups[ids[1]][-1].end_point.line_number
            column_n = groups[ids[1]][-1].end_point.column_number
            end_line_part = source_lines[line_n][column_n:]
            if "//" not in end_line_part and any(c not in noneffective for c in end_line_part):
                return not slice_predicate.lines_are_full
    return True


def __build_general_groups(general_statements):
    last_general_group = []
    general_groups = []
    for statement in general_statements:
        if statement.statement_type in {
            StatementType.UNKNOWN, StatementType.ASSIGNMENT, StatementType.VARIABLE, StatementType.CALL
        }:
            last_general_group.append(statement)
        else:
            if last_general_group:
                general_groups.append(last_general_group)
            general_groups.append([statement])
            last_general_group = []
    if last_general_group:
        general_groups.append(last_general_group)

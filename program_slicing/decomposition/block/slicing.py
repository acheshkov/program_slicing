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
from program_slicing.graph.statement import Statement


def get_block_slices(
        source_code: str,
        lang: str,
        slice_predicate: SlicePredicate = None,
        include_noneffective: bool = True,
        may_cause_code_duplication: bool = False) -> Iterable[ProgramSlice]:
    """
    For each a specified source code generate list of Program Slices based on continues blocks.
    :param source_code: source code that should be decomposed.
    :param lang: string with the source code format described as a file ext (like '.java' or '.xml').
    :param slice_predicate: SlicePredicate object that describes which slices should be filtered. No filtering if None.
    :param include_noneffective: include comments and blank lines to a slice if True.
    :param may_cause_code_duplication: allow to generate slices which extraction will cause code duplication if True.
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
            for statement in manager.general_statements
            if statement in statements_in_scope),
            key=lambda x: (x.start_point, -x.end_point))
        id_combinations = (
            c for c in combinations_with_replacement([idx for idx in range(len(general_statements))], 2)
            if __pre_check(general_statements, c, slice_predicate, source_lines)
        )
        for ids in id_combinations:
            current_statements = general_statements[ids[0]: ids[1] + 1]
            if not current_statements:
                continue
            extended_statements = manager.get_statements_in_range(
                current_statements[0].start_point,
                current_statements[-1].end_point)
            if not may_cause_code_duplication:
                affecting_statements = manager.get_affecting_statements(extended_statements)
                if len(manager.get_used_variables(affecting_statements)) > 1 or \
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
        statements: List[Statement],
        ids: Tuple[int, ...],
        slice_predicate: SlicePredicate,
        source_lines: List[str]) -> bool:
    if slice_predicate:
        if slice_predicate.min_amount_of_lines is not None:
            max_lines_number = \
                statements[ids[1]].end_point.line_number - statements[ids[0]].start_point.line_number + 1
            if max_lines_number < slice_predicate.min_amount_of_lines:
                return False
        if slice_predicate.max_amount_of_statements is not None:
            min_statements_number = ids[1] - ids[0] + 1
            if min_statements_number > slice_predicate.max_amount_of_statements:
                return False
        if slice_predicate.lines_are_full is not None:
            line_n = statements[ids[0]].start_point.line_number
            column_n = statements[ids[0]].start_point.column_number
            line_part = source_lines[line_n][:column_n]
            if "//" not in line_part and any(c != ' ' and c != '\t' and c != '\n' and c != '\r' for c in line_part):
                return not slice_predicate.lines_are_full
            line_n = statements[ids[1]].end_point.line_number
            column_n = statements[ids[1]].end_point.column_number
            line_part = source_lines[line_n][column_n:]
            if "//" not in line_part and any(c != ' ' and c != '\t' and c != '\n' and c != '\r' for c in line_part):
                return not slice_predicate.lines_are_full
    return True

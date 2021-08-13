__licence__ = 'MIT'
__author__ = 'lyriccoder'
__credits__ = ['lyriccoder, kuyaki']
__maintainer__ = 'lyriccoder'
__date__ = '2021/05/20'

from itertools import combinations_with_replacement
from typing import Iterable

from program_slicing.decomposition.program_slice import ProgramSlice
from program_slicing.decomposition.slice_predicate import SlicePredicate
from program_slicing.graph.manager import ProgramGraphsManager


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
    for scope in manager.scope_statements:
        function_statement = manager.get_function_statement(scope)
        if function_statement is None:
            continue
        function_length = function_statement.end_point.line_number - function_statement.start_point.line_number + 1
        general_statements = sorted((
            statement
            for statement in manager.get_statements_in_scope(scope)
            if statement in manager.general_statements),
            key=lambda x: (x.start_point, -x.end_point))
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
                affecting_statements = manager.get_affecting_statements(extended_statements)
                if len(manager.get_used_variables(affecting_statements)) > 1 or \
                        manager.contain_redundant_statements(extended_statements):
                    continue
            if len(manager.get_exit_statements(extended_statements)) > 1:
                continue
            program_slice = ProgramSlice(source_lines).from_statements(extended_statements)
            if slice_predicate is None or slice_predicate(program_slice):
                yield program_slice


def __percentage_or_amount_exceeded(outer_number, inner_number, percentage):
    return float(inner_number) / outer_number > percentage or inner_number > outer_number - 4

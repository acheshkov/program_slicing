__licence__ = 'MIT'
__author__ = 'lyriccoder'
__credits__ = ['lyriccoder, kuyaki']
__maintainer__ = 'lyriccoder'
__date__ = '2021/05/20'

from itertools import combinations_with_replacement, filterfalse
from typing import Iterable

from program_slicing.decomposition.filter_for_block_slicing_algorithm import check_all_lines_are_full, check_parsing, \
    check_min_amount_of_lines
from program_slicing.decomposition.program_slice import ProgramSlice
from program_slicing.decomposition.slice_predicate import SlicePredicate
from program_slicing.graph.manager import ProgramGraphsManager


def get_block_slices(
        source_code: str,
        lang: str,
        min_lines_number=1,
        min_statements_number=1,
        max_percentage_of_lines: float = None,
        may_cause_code_duplication: bool = False) -> Iterable[ProgramSlice]:
    """
    For each a specified source code generate list of Program Slices based on continues blocks.
    :param source_code: source code that should be decomposed.
    :param lang: string with the source code format described as a file ext (like '.java' or '.xml').
    :param max_percentage_of_lines: number of lines in each slice shouldn't exceed a corresponding
    share of source lines specified by float number [0.0, 1.0].
    :param may_cause_code_duplication: allow to generate slices which extraction will cause code duplication if True.
    :return: generator of the ProgramSlices.
    """
    source_lines = source_code.split("\n")
    manager = ProgramGraphsManager(source_code, lang)
    all_block_slices = []
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

            pg = ProgramSlice(source_lines).from_statements(
                extended_statements,
                # general_statements=manager.general_statements,
                cfg=manager.get_control_flow_graph(),
            )
            if pg.cfg:
                print(1)
            else:
                print(2)
            all_block_slices.append(pg)


    filtered_block_slices = list(
        filterfalse(lambda x: check_min_amount_of_lines(x, min_lines_number), all_block_slices))
    # filtered_block_slices = filter(lambda x: check_min_amount_of_statements(x, min_statements_number), filtered_block_slices)
    filtered_block_slices = list(filter(lambda x: check_all_lines_are_full(x), filtered_block_slices))
    filtered_block_slices = list(filter(lambda x: check_parsing(x, lang), filtered_block_slices))
    return filtered_block_slices
    # if slice_predicate is None or slice_predicate(program_slice, scopes=manager.scope_statements):
    #     yield program_slice


def __percentage_or_amount_exceeded(outer_number, inner_number, percentage):
    #  (outer_number - 3) is number of lines in regular function body
    #  so that we also check that not all the lines from body are included.
    return float(inner_number) / outer_number > percentage or inner_number > outer_number - 4

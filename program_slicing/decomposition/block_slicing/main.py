__licence__ = 'MIT'
__author__ = 'lyriccoder'
__credits__ = ['lyriccoder, kuyaki']
__maintainer__ = 'lyriccoder'
__date__ = '2021/05/20'

from itertools import combinations_with_replacement, filterfalse
from typing import Iterable

from program_slicing.decomposition.block_slicing.filter_for_block_slicing_algorithm import (
    check_all_lines_are_full, check_parsing, check_min_amount_of_lines,
    does_slice_match_scope, does_have_multiple_return)
from program_slicing.decomposition.program_slice import ProgramSlice
from program_slicing.graph.manager import ProgramGraphsManager


def get_block_slices(
        source_code: str,
        lang: str,
        min_lines_number=1,
        min_statements_number=1,
        max_percentage_of_lines: float = None,
        filter_by_scope: bool = False) -> Iterable[ProgramSlice]:
    """
    For each a specified source code generate list of Program Slices based on continues blocks.
    :param filter_by_scope: filters scopes if they do not match block (if block, while block, etc.)
    :param source_code: source code that should be decomposed.
    :param lang: string with the source code format described as a file ext (like '.java' or '.xml').
    :param max_percentage_of_lines: number of lines in each slice shouldn't exceed a corresponding
    share of source lines specified by float number [0.0, 1.0].
    :return: generator of the ProgramSlices.
    """
    source_lines = source_code.split("\n")
    source_code_bytes = bytes(source_code, 'utf-8')
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
            cur_lines = (current_statements[0].start_point.line_number + 1, current_statements[-1].end_point.line_number + 1)
            print(cur_lines)
            if cur_lines[0]==16 and cur_lines[1] == 24:
                print(1)
            emos_lines_number = current_statements[-1].end_point.line_number - current_statements[0].start_point.line_number + 1  # noqa: E50
            if max_percentage_of_lines is not None and percentage_or_amount_exceeded(
                    function_length,
                    emos_lines_number,
                    max_percentage_of_lines):
                continue

            extended_statements = manager.get_statements_in_range(
                current_statements[0].start_point,
                current_statements[-1].end_point)
            # extended_statements = list(filter(lambda x: x.ast_node_type == 'block', extended_statements))
            if extended_statements:
                # need to filter shitty emos surrounded by brackets like { for (String s: asrgs) {} }
                ps = ProgramSlice(source_lines, source_code_bytes=source_code_bytes).from_statements_lightweight(
                    extended_statements,
                    # general_statements=manager.general_statements,
                )
                # print(ps.ranges[0][0].line_number, ps.ranges[-1][1].line_number)
                all_block_slices.append(ps)

    return run_filters(all_block_slices, manager, min_lines_number, filter_by_scope, lang)


def is_invalid_output_params(manager, ps: ProgramSlice):
    """
    Checks if program slice will have to return 2 variables if we extract it
    :param manager: ProgramGraphsManager
    :param ps: program slice to extract
    :return: True if it is invalid, false otherwise
    """
    affecting_statements = manager.get_affecting_statements(ps.statements)
    if len(manager.get_used_variables(affecting_statements)) > 1 or \
            manager.contain_redundant_statements(ps.statements):
        return True
    return False


def percentage_or_amount_exceeded(outer_number: int, inner_number: int, percentage: float):
    #  (outer_number - 3) is number of lines in regular function body
    #  so that we also check that not all the lines from body are included.
    return float(inner_number) / outer_number > percentage or inner_number > outer_number - 4


def run_filters(
        all_block_slices: Iterable[ProgramSlice],
        manager: ProgramGraphsManager,
        min_lines_number: int,
        filter_by_scope: bool,
        lang: str):
    """
    Run all needed filters.

    """
    # filtered_block_slices = filter(lambda x: check_min_amount_of_statements(x, min_statements_number), filtered_block_slices)  # noqa: E50
    filtered_block_slices = list(filter(lambda x: check_min_amount_of_lines(x, min_lines_number), all_block_slices))
    if filter_by_scope:
        filtered_block_slices = list(
            filter(lambda x: does_slice_match_scope(manager.scope_statements, x), filtered_block_slices))
    filtered_block_slices = list(filterfalse(
        lambda x: does_have_multiple_return(manager, x), filtered_block_slices))
    filtered_block_slices = list(filterfalse(
        lambda x: is_invalid_output_params(manager, x), filtered_block_slices))
    filtered_block_slices = list(filter(lambda x: check_all_lines_are_full(x), filtered_block_slices))
    filtered_block_slices = list(filter(lambda x: check_parsing(x, lang), filtered_block_slices))

    return filtered_block_slices

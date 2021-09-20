__licence__ = 'MIT'
__author__ = 'lyriccoder'
__credits__ = ['lyriccoder, kuyaki']
__maintainer__ = 'lyriccoder'
__date__ = '2021/05/20'

from itertools import combinations_with_replacement, filterfalse
from typing import Iterable

from program_slicing.decomposition.block_slicing.filter_for_block_slicing_algorithm import (
    check_all_lines_are_full, check_parsing, check_min_amount_of_lines,
    does_slice_match_scope, has_multiple_exit_nodes)
from program_slicing.decomposition.program_slice import ProgramSlice
from program_slicing.graph.manager import ProgramGraphsManager
from datetime import datetime

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
    manager = ProgramGraphsManager(source_code, lang)
    start_time = datetime.now()
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

            emos_lines_number = current_statements[-1].end_point.line_number - current_statements[0].start_point.line_number + 1  # noqa: E50
            if max_percentage_of_lines is not None and percentage_or_amount_exceeded(
                    function_length,
                    emos_lines_number,
                    max_percentage_of_lines):
                continue
            extended_statements = manager.get_statements_in_range(
                current_statements[0].start_point,
                current_statements[-1].end_point)

            ps = ProgramSlice(source_lines).from_statements(
                extended_statements
            )
            all_block_slices.append(ps)

    d = {'emos_generation_time': (len(all_block_slices), (datetime.now() - start_time).seconds)}
    return run_filters(all_block_slices, manager, min_lines_number, filter_by_scope, lang, d)


def has_multiple_output_params(manager, ps: ProgramSlice):
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
        lang: str,
        filters_used):
    """
    Run all needed filters.

    """
    filters_used['all_non_filtered_emos'] = (len(all_block_slices), 0.00)
    # filtered_block_slices = filter(lambda x: check_min_amount_of_statements(x, min_statements_number), filtered_block_slices)  # noqa: E50
    start_absolute = datetime.now()
    filtered_block_slices = list(filterfalse(lambda x: check_min_amount_of_lines(x, min_lines_number), all_block_slices))
    end = datetime.now()
    filters_used['check_min_amount_of_lines'] = \
        (len(all_block_slices) - len(filtered_block_slices), (end - start_absolute).seconds)
    if filter_by_scope:
        # start = datetime.now()
        filtered_block_slices = list(filter(lambda x: does_slice_match_scope(manager.scope_statements, x), filtered_block_slices))
        # end = datetime.now()
        # filters_used['does_slice_match_scope'] = (filters_used['check_min_amount_of_lines'] - len(filtered_block_slices), (end - start).microseconds)

    start = datetime.now()
    prev = len(filtered_block_slices)
    filtered_block_slices = list(filterfalse(
        lambda x: has_multiple_exit_nodes(manager, x), filtered_block_slices))
    end = datetime.now()
    filters_used['has_multiple_exit_nodes'] = (prev - len(filtered_block_slices), (end - start).seconds)

    prev = len(filtered_block_slices)
    start = datetime.now()
    filtered_block_slices = list(filterfalse(
        lambda x: has_multiple_output_params(manager, x), filtered_block_slices))
    end = datetime.now()
    filters_used['has_multiple_output_params'] = (prev - len(filtered_block_slices), (end - start).seconds)
    prev = len(filtered_block_slices)
    start = datetime.now()
    filtered_block_slices = list(filter(lambda x: check_all_lines_are_full(x), filtered_block_slices))
    end = datetime.now()
    filters_used['check_all_lines_are_full'] = (prev - len(filtered_block_slices), (end - start).seconds)
    prev = len(filtered_block_slices)
    start = datetime.now()
    filtered_block_slices = list(filter(lambda x: check_parsing(x, lang), filtered_block_slices))
    end = datetime.now()
    filters_used['check_parsing'] = (prev - len(filtered_block_slices), (end - start).seconds)
    # filters_used['total_time_filtration']
    return filters_used, filtered_block_slices

__licence__ = 'MIT'
__author__ = 'KatGarmash'
__credits__ = ['KatGarmash', 'kuyaki']
__maintainer__ = 'KatGarmash'
__date__ = '2021/10/18'

from collections import defaultdict
from functools import reduce
from typing import List, Set, Dict

from program_slicing.decomposition.block.extension.slicing import __get_incoming_variables, __get_outgoing_variables
from program_slicing.decomposition.program_slice import ProgramSlice
from program_slicing.graph.manager import ProgramGraphsManager
from program_slicing.graph.parse import Lang
from program_slicing.graph.statement import Statement, StatementType


def length_score_hh(
        source_lines: List[str],
        extraction: ProgramSlice,
        line_weight: float = 0.1,
        max_score_length: int = 3) -> float:
    """
    Length scoring function from Haas&Hummel 2016:
    S_length = min (c_l · min (L_c, L_r), MAX_scoreLength),
    L_c -- length of extraction, L_r -- length of remainder,
    c_l = 0.1 , MAX_scoreLength = 3 (from paper)
    :return: score value
    """
    length_extraction = reduce(lambda x, y: x + y[1].line_number - y[0].line_number + 1, extraction.ranges_compact, 0)
    length_remainder = len(source_lines) - length_extraction - 1
    return min(line_weight * min(length_extraction, length_remainder), max_score_length)


def nesting_depth_score_hh(
        extraction: ProgramSlice,
        statement_to_depth: Dict[Statement, int] = None,
        method_statements: Set[Statement] = None) -> int:
    """
    Nesting depth score from Haas&Hummel 2016:
    S_nestDepth = min (Dm − Dr,Dm − Dc),
    D_m - depth of orig method, D_r - of remainder, D_c - of extraction
    :return:
    """
    manager = extraction.context
    if method_statements is None:
        extraction_general_statements = sorted(
            extraction.general_statements,
            key=lambda x: (x.start_point, -x.end_point))
        if not extraction_general_statements:
            raise ValueError("Couldn't find general statements in extraction slice")
        method_statement = manager.get_function_statement(extraction_general_statements[0])
        method_statements = [
            statement
            for statement in manager.get_statements_in_range(method_statement.start_point, method_statement.end_point)
            if statement in manager.general_statements
        ]
    if statement_to_depth is None:
        statement_to_depth = dict()
    max_depth_method = max([
        __nesting_depth_recursive(statement, manager, statement_to_depth)
        for statement in method_statements
    ])
    min_depth_extraction = min([
        __nesting_depth_recursive(statement, manager, statement_to_depth)
        for statement in extraction.general_statements
    ])
    max_depth_extraction = max([
        __nesting_depth_recursive(statement, manager, statement_to_depth)
        for statement in extraction.general_statements
    ]) - min_depth_extraction
    remainder_statements = set(method_statements).difference(set(extraction.general_statements))
    max_depth_remainder = max([
        __nesting_depth_recursive(statement, manager, statement_to_depth)
        for statement in remainder_statements
    ])
    return min(max_depth_method - max_depth_extraction, max_depth_method - max_depth_remainder)


def nesting_area_score_hh(
        extraction: ProgramSlice,
        statement_to_depth: Dict[Statement, int] = None,
        method_statements: Set[Statement] = None) -> float:
    """
    A_reduction = min (Am − Ac,Am − Ar),
    Am - nesting area of original method, A_c - of extraction, A_r - of remainder
    S_nextArea = 2 * D_m * (A_reduction / A_m),
    D_m - depth of orig method
    """
    manager = extraction.context
    if statement_to_depth is None:
        statement_to_depth = dict()
    if method_statements is None:
        extraction_general_statements = sorted(
            extraction.general_statements,
            key=lambda x: (x.start_point, -x.end_point))
        if not extraction_general_statements:
            raise ValueError("Couldn't find general statements in extraction slice")
        method_statement = manager.get_function_statement(extraction_general_statements[0])
        method_statements = [
            statement
            for statement in manager.get_statements_in_range(method_statement.start_point, method_statement.end_point)
            if statement in manager.general_statements
        ]

    general_statements_by_line = defaultdict(lambda: set())
    for statement in method_statements:
        if statement.statement_type == StatementType.SCOPE:
            continue
        general_statements_by_line[statement.start_point.line_number].add(statement)
    real_statements_all = set()
    for k, statements in general_statements_by_line.items():
        _widest = list(sorted(
            statements,
            key=lambda x: (x.start_point.column_number, -x.end_point.line_number, -x.end_point.column_number)))[0]
        real_statements_all.add(_widest)
    real_statements_extraction = real_statements_all.intersection(extraction.general_statements)
    real_statements_remainder = real_statements_all.difference(real_statements_extraction)

    area_method = sum([
        __nesting_depth_recursive(statement, manager, statement_to_depth)
        for statement in real_statements_all
    ])
    min_depth_extraction = min([
        __nesting_depth_recursive(statement, manager, statement_to_depth)
        for statement in real_statements_extraction
    ])
    area_extraction = sum([
        __nesting_depth_recursive(statement, manager, statement_to_depth) - min_depth_extraction
        for statement in real_statements_extraction
    ])
    area_remainder = sum([
        __nesting_depth_recursive(statement, manager, statement_to_depth)
        for statement in real_statements_remainder
    ]) + min_depth_extraction
    area_reduction = min(area_method - area_remainder, area_method - area_extraction)
    max_depth_orig = max(
        [__nesting_depth_recursive(statement, manager, statement_to_depth) for statement in real_statements_all])
    return 2 * max_depth_orig * (area_reduction / area_method)


def parameters_score_hh(
        extraction: ProgramSlice,
        max_score: int = 4) -> int:
    """
    Parameter scoring function from Haas&Hummel 2016:
    S_param = MAX_scoreParam − n_in − n_out
    n_in, n_out - number of in/out parameters for extraction
    MAX_scoreParam = 4 (from paper)
    :return:
    """
    manager = extraction.context
    extraction_statements = extraction.statements
    n_in = len(__get_incoming_variables(extraction_statements, manager))
    n_out = len(__get_outgoing_variables(extraction_statements, manager))
    return max_score - n_out - n_in


def aggregate_score_hh(
        source_code: str,
        extraction: ProgramSlice,
        nesting_area_hh: int = None,
        nesting_depth_hh: float = None,
        length_hh: float = None,
        params_hh: int = None):
    if nesting_area_hh is None or nesting_depth_hh is None:
        manager = extraction.context
        statement_to_depth = dict()
        extraction_general_statements = sorted(
            extraction.general_statements,
            key=lambda x: (x.start_point, -x.end_point))
        if not extraction_general_statements:
            raise ValueError("Couldn't find general statements in extraction slice")
        method_statement = manager.get_function_statement(extraction_general_statements[0])
        method_statements = [
            statement
            for statement in
            manager.get_statements_in_range(method_statement.start_point, method_statement.end_point)
            if statement in manager.general_statements
        ]
        nesting_depth_hh = nesting_depth_score_hh(extraction, statement_to_depth, method_statements)
        nesting_area_hh = nesting_area_score_hh(extraction, statement_to_depth, method_statements)
    if length_hh is None:
        length_hh = length_score_hh(source_code.split("\n"), extraction)
    if params_hh is None:
        params_hh = parameters_score_hh(extraction)
    return nesting_depth_hh + nesting_area_hh + length_hh + params_hh


def score_silva_vars(extraction: ProgramSlice):
    #def_and_ref_vars =
    pass


def __nesting_depth_recursive(statement: Statement, manager: ProgramGraphsManager, result: Dict[Statement, int]) -> int:
    if statement in result:
        return result[statement]
    if statement.statement_type == StatementType.FUNCTION:
        result[statement] = -1
        return -1
    cdg = manager.control_dependence_graph
    if statement not in cdg:
        result[statement] = -1
        return -1
    parents_d = [
        __nesting_depth_recursive(parent, manager=manager, result=result)
        for parent in cdg.predecessors(statement)
    ]
    if not parents_d:
        result[statement] = -1
        return -1
    return max(parents_d) + 1


def __distance_silva(dependency_set_1: Set, dependency_set_2: Set) -> float:
    set_intersection = dependency_set_1.intersection(dependency_set_2)
    diff_1 = dependency_set_1.difference(dependency_set_2)
    diff_2 = dependency_set_2.difference(dependency_set_1)
    return 1 - 0.5 * (len(set_intersection) / (len(set_intersection) + len(diff_1)) +\
                      len(set_intersection) / (len(set_intersection) + len(diff_2)))

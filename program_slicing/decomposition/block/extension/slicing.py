__licence__ = 'MIT'
__author__ = 'KatGarmash'
__credits__ = ['KatGarmash', 'kuyaki']
__maintainer__ = 'KatGarmash'
__date__ = '2021/09/14'

from functools import reduce
from itertools import chain, combinations_with_replacement, combinations
from typing import Set, Tuple, Dict, List, Iterator

from program_slicing.decomposition.program_slice import ProgramSlice
from program_slicing.decomposition.slice_predicate import SlicePredicate
from program_slicing.decomposition.variable.slicing import __obtain_extension, __obtain_necessary_goto
from program_slicing.graph.cdg import ControlDependenceGraph
from program_slicing.graph.ddg import DataDependenceGraph
from program_slicing.graph.manager import ProgramGraphsManager
from program_slicing.graph.parse import Lang
from program_slicing.graph.point import Point
from program_slicing.graph.statement import Statement, StatementType


VariableDefinition = Statement
VariableUse = Statement
SingletonExtensions = List[Tuple[
    Set[Statement],
    Dict[str, VariableUse],
    Dict[str, VariableDefinition],
    str
]]


def get_extended_block_slices(
        source_code: str,
        lang: Lang,
        slice_predicate: SlicePredicate = None) -> Set[ProgramSlice]:
    manager = ProgramGraphsManager(source_code, lang)
    source_lines = source_code.split("\n")
    slices_so_far = set()
    for raw_block in __temp__get_block_slice_statements_raw(manager):
        for extended_block in __get_block_extensions(raw_block, manager, source_lines):
            if slice_predicate is None or slice_predicate(extended_block, context=manager):
                slices_so_far.add(extended_block)
    return slices_so_far


def get_extended_block_slices_ordered(code_ex: str, slice_to_expand: Tuple[int, int]) -> Set[ProgramSlice]:
    raise NotImplementedError("ordering not implemented yet")


def __get_block_extensions(
        block_statements: Set[Statement],
        manager: ProgramGraphsManager,
        source_lines: List[str]) -> Set[ProgramSlice]:
    singleton_extensions = __extend_block_singleton(block_statements, manager)
    result = set()
    for variable_id_subset in chain.from_iterable(
            combinations(range(len(singleton_extensions)), r)
            for r in range(1, len(singleton_extensions) + 1)):
        full_extension: Set[Statement] = reduce(
            lambda x, y: x.union(singleton_extensions[y][0]),
            variable_id_subset,
            set())
        extension_program_slice = ProgramSlice(source_lines).from_statements(full_extension)
        if extension_program_slice not in result:
            if __filter_valid(full_extension, block_statements, manager):
                result.add(extension_program_slice)
    if __filter_valid(block_statements, block_statements, manager):
        block_slice = ProgramSlice(source_lines).from_statements(block_statements)
        result.add(block_slice)
    return result


def __get_continuous_range_extensions(
        source_code: str,
        line_range: Tuple[int, int],
        lang: Lang) -> Set[ProgramSlice]:
    manager = ProgramGraphsManager(source_code, lang)
    block_statements = manager.get_statements_in_range(
        Point(line_range[0], 0),
        Point(line_range[1], 10000))
    return __get_block_extensions(block_statements, manager, source_code.split("\n"))


def __temp__get_block_slice_statements_raw(manager: ProgramGraphsManager) -> Iterator[Set[Statement]]:
    for scope in manager.scope_statements:
        function_statement = manager.get_function_statement(scope)
        if function_statement is None:
            continue
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
            extended_statements = manager.get_statements_in_range(
                current_statements[0].start_point,
                current_statements[-1].end_point)
            yield extended_statements


def __get_incoming_variables(
        block_statements: Set[Statement],
        manager: ProgramGraphsManager) -> Dict[str, VariableUse]:
    """
    Identify variables that should be incoming parameters if block_statements
    is extracted into a separate method.
    :param block_statements: block to look for variables in
    :param manager: manage for graphs of the whole program
    :return: dictionary from name of variable in the block to a statement
    in a block that uses it and is data-dependent on a statement outside the block
    """
    ddg = manager.data_dependence_graph
    incoming_variables = dict()
    for statement in block_statements:
        for data_dom in ddg.predecessors(statement):
            # can be multimap, but it's ok for our purposes
            if data_dom not in block_statements and data_dom.name not in incoming_variables:
                if __flow_dep_given_data_dep(statement, data_dom):
                    incoming_variables[data_dom.name] = statement
    return incoming_variables


def __get_outgoing_variables(
        block_statements: Set[Statement],
        manager: ProgramGraphsManager) -> Dict[str, VariableDefinition]:
    ddg = manager.data_dependence_graph
    outgoing_variables: Dict[str, VariableDefinition] = dict()
    for statement in block_statements:
        for data_dependent in set(ddg.successors(statement)).difference(block_statements):
            if __flow_dep_given_data_dep(data_dependent, statement):
                outgoing_variables[statement.name] = statement
                break
    return outgoing_variables


def __flow_dep_given_data_dep(
        statement_1: Statement,
        statement_2: Statement,
        variable_name: str = None) -> bool:
    """
    Check if statement_1 is flow-dependent on statement_2 assuming that they are data dependent.
    :param statement_1: statement that is supposed to be flow-dependent.
    :param statement_2: statement that is supposed to be flow-dominant.
    :param variable_name: flow-dependence with respect to variable variable_name.
    :return: true if there is flow dependence.
    """
    if statement_2.statement_type not in {
        StatementType.ASSIGNMENT,
        StatementType.VARIABLE,
        StatementType.FUNCTION
    }:
        return False
    if statement_1.name != statement_2.name:
        if variable_name is not None:
            return statement_2.name == variable_name
        return True
    return False


def __add_statement_to_slice(
        statement: Statement,
        backward_slice: Set[Statement],
        manager: ProgramGraphsManager) -> None:
    if statement in backward_slice:
        return
    backward_slice.add(statement)
    for goto_statement in __obtain_necessary_goto(manager, statement):
        __add_statement_to_slice(goto_statement, backward_slice, manager)
    for extension_statement in __obtain_extension(manager, statement, region=None):
        if extension_statement.statement_type == StatementType.SCOPE:
            backward_slice.add(extension_statement)
        else:
            __add_statement_to_slice(extension_statement, backward_slice, manager)


def __compute_backward_slice_recursive(
        statement: Statement,
        variable_name: str,
        original_block: Set[Statement],
        cdg: ControlDependenceGraph,
        ddg: DataDependenceGraph,
        backward_slice: Set,
        manager: ProgramGraphsManager) -> None:
    __add_statement_to_slice(statement, backward_slice, manager)
    cdg_predecessors = cdg.predecessors(statement)
    flow_predecessors = filter(
        lambda x: __flow_dep_given_data_dep(statement, x, variable_name=variable_name),
        ddg.predecessors(statement))
    for predecessor in set(chain(cdg_predecessors, flow_predecessors)):
        if predecessor.statement_type == StatementType.FUNCTION:
            continue
        new_variable_name = None
        if predecessor in original_block:
            new_variable_name = variable_name
        __compute_backward_slice_recursive(
            predecessor,
            new_variable_name,
            original_block,
            cdg,
            ddg,
            backward_slice,
            manager)


def __compute_backward_slice(
        variable_use: VariableUse,
        variable_name: str,
        original_block: Set[Statement],
        manager: ProgramGraphsManager) -> Set[Statement]:
    backward_slice: Set[Statement] = set()
    cdg = manager.control_dependence_graph
    ddg = manager.data_dependence_graph
    __compute_backward_slice_recursive(
        variable_use,
        variable_name,
        original_block,
        cdg,
        ddg,
        backward_slice,
        manager)
    return backward_slice


def __compute_forward_slice_recursive(
        variable_def: VariableDefinition,
        forward_slice: Set[Statement],
        ddg: DataDependenceGraph,
        recursion: bool) -> None:
    for data_successor in ddg.successors(variable_def):
        if data_successor.statement_type == StatementType.ASSIGNMENT:
            if recursion:
                forward_slice.add(data_successor)
                __compute_forward_slice_recursive(data_successor, forward_slice, ddg, recursion)
            else:
                continue
        else:
            forward_slice.add(data_successor)


def __compute_forward_slice(
        variable_def: VariableDefinition,
        manager: ProgramGraphsManager) -> Set[Statement]:
    forward_slice = set()
    ddg = manager.data_dependence_graph
    __compute_forward_slice_recursive(
        variable_def,
        forward_slice,
        ddg,
        recursion=(variable_def.statement_type == StatementType.VARIABLE))
    return forward_slice


def __extend_block_singleton(
        block_statements: Set[Statement],
        manager: ProgramGraphsManager) -> SingletonExtensions:
    incoming_variables = __get_incoming_variables(block_statements, manager)
    outgoing_variables = __get_outgoing_variables(block_statements, manager)
    singleton_extensions: SingletonExtensions = list()
    for var_name in chain(incoming_variables.keys(), outgoing_variables.keys()):
        new_block = block_statements.copy()
        new_incoming_variables = incoming_variables.copy()
        new_outgoing_variables = outgoing_variables.copy()
        if var_name in incoming_variables:
            variable_use = incoming_variables[var_name]
            backward_slice = __compute_backward_slice(variable_use, var_name, block_statements, manager)
            new_block |= backward_slice
            del new_incoming_variables[var_name]
        if var_name in outgoing_variables:
            variable_def = outgoing_variables[var_name]
            forward_slice = __compute_forward_slice(variable_def, manager)
            new_block |= forward_slice
            del new_outgoing_variables[var_name]
        singleton_extensions.append((
            new_block,
            new_incoming_variables,
            new_outgoing_variables,
            var_name))
    return singleton_extensions


def __filter_anti_dependence(
        new_statements: Set[Statement],
        original_statements: Set[Statement],
        manager: ProgramGraphsManager) -> bool:
    ddg = manager.data_dependence_graph
    for statement in new_statements:
        for data_successor in ddg.successors(statement):
            if data_successor in original_statements.union(new_statements):
                continue
            if __flow_dep_given_data_dep(data_successor, statement):
                return False
    return True


def __filter_control_dependence(
        new_statements: Set[Statement],
        original_statements: Set[Statement],
        manager: ProgramGraphsManager) -> bool:
    cdg = manager.control_dependence_graph
    for statement in new_statements:
        for control_successor in cdg.successors(statement):
            if control_successor not in new_statements.union(original_statements):
                return False
        for control_predecessor in cdg.predecessors(statement):
            if control_predecessor.statement_type == StatementType.FUNCTION:
                continue
            if control_predecessor not in new_statements.union(original_statements):
                return False
    return True


def __filter_more_than_one_outgoing(
        slice_candidate: Set[Statement],
        manager: ProgramGraphsManager) -> bool:
    outgoing_variables = __get_outgoing_variables(slice_candidate, manager)
    return len(outgoing_variables.keys()) <= 1


def __filter_valid(
        slice_candidate: Set[Statement],
        original_statements: Set[Statement],
        manager: ProgramGraphsManager) -> bool:
    new_statements = slice_candidate.difference(original_statements)
    if not __filter_anti_dependence(new_statements, original_statements, manager):
        return False
    if not __filter_more_than_one_outgoing(slice_candidate, manager):
        return False
    if not __filter_control_dependence(new_statements, original_statements, manager):
        return False
    return True

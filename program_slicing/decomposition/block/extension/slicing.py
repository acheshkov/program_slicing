__licence__ = 'MIT'
__author__ = 'KatGarmash'
__credits__ = ['KatGarmash', 'kuyaki']
__maintainer__ = 'KatGarmash'
__date__ = '2021/09/14'

from functools import reduce
from itertools import chain, combinations
from typing import Set, Tuple, Dict, List

from program_slicing.decomposition.block.slicing import get_block_slices_from_manager
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
        slice_predicate: SlicePredicate = None,
        include_noneffective: bool = True) -> Set[ProgramSlice]:
    """
    For each a specified source code generate list of Program Slices based on extended continuous blocks.
    :param source_code: source code that should be decomposed.
    :param lang: the source code Lang.
    :param slice_predicate: SlicePredicate object that describes which slices should be filtered. No filtering if None.
    :param include_noneffective: include comments and blank lines to a slice if True.
    :return: set of the ProgramSlices.
    """
    manager = ProgramGraphsManager(source_code, lang)
    source_lines = source_code.split("\n")
    slices_so_far = set()
    for raw_block in get_block_slices_from_manager(
            source_lines,
            manager,
            include_noneffective=include_noneffective,
            unite_statements_into_groups=False):
        raw_block_statements = set(filter(lambda x: x.statement_type != StatementType.EXIT, raw_block.statements))
        for extended_block in __get_block_extensions(
                raw_block_statements,
                manager,
                source_lines,
                include_noneffective=include_noneffective):
            if slice_predicate is None or slice_predicate(extended_block, context=manager):
                slices_so_far.add(extended_block)
    return slices_so_far


def get_extended_block_slices_ordered(code_ex: str, slice_to_expand: Tuple[int, int]) -> Set[ProgramSlice]:
    raise NotImplementedError("ordering not implemented yet")


def get_continuous_range_extensions(
        source_code: str,
        line_range: Tuple[int, int],
        lang: Lang) -> Set[ProgramSlice]:
    """
    API to generate all extensions based on provided line range.
    :param source_code: source code that should be decomposed.
    :param line_range: range of line numbers in source code.
    :param lang: the source code Lang.
    :return: set of the ProgramSlices.
    """
    manager = ProgramGraphsManager(source_code, lang)
    block_statements = manager.get_statements_in_range(
        Point(line_range[0], 0),
        Point(line_range[1], 10000))
    return __get_block_extensions(block_statements, manager, source_code.split("\n"))


def __get_block_extensions(
        block_statements: Set[Statement],
        manager: ProgramGraphsManager,
        source_lines: List[str],
        include_noneffective: bool = True) -> Set[ProgramSlice]:
    singleton_extensions = __extend_block_singleton(block_statements, manager)
    result = set()
    for variable_id_subset in chain.from_iterable(
            combinations(range(len(singleton_extensions)), r)
            for r in range(1, len(singleton_extensions) + 1)):
        full_extension: Set[Statement] = reduce(
            lambda x, y: x.union(singleton_extensions[y][0]),
            variable_id_subset,
            set())
        extension_program_slice = ProgramSlice(
            source_lines,
            context=manager if include_noneffective else None).from_statements(full_extension)
        if extension_program_slice not in result:
            if len(manager.get_exit_statements(full_extension)) > 1:
                continue
            if not __filter_valid(full_extension, manager, original_statements=block_statements):
                continue
            if not __full_control_construction(full_extension, manager):
                continue
            result.add(extension_program_slice)
    if __filter_valid(block_statements, manager) and __full_control_construction(block_statements, manager):
        block_slice = ProgramSlice(
            source_lines,
            context=manager if include_noneffective else None).from_statements(block_statements)
        result.add(block_slice)
    return result


def __full_control_construction(statements: Set[Statement], manager: ProgramGraphsManager) -> bool:
    for statement in statements:
        scope_statement = manager.get_scope_statement(statement)
        if scope_statement is None:
            continue
        if scope_statement.statement_type in {StatementType.LOOP, StatementType.BRANCH, StatementType.GOTO} and \
                scope_statement not in statements:
            return False
    return True


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
        if statement.statement_type == StatementType.FUNCTION:
            continue
        for data_dom in ddg.predecessors(statement):
            # can be multimap, but it's ok for our purposes
            if data_dom not in block_statements and data_dom.name not in incoming_variables:
                if __flow_dep_given_data_dep(statement, data_dom):
                    # FIXME: what if one variable has been passed to several different statements?
                    incoming_variables[data_dom.name] = statement
    return incoming_variables


def __get_outgoing_variables(
        block_statements: Set[Statement],
        manager: ProgramGraphsManager) -> Dict[str, VariableDefinition]:
    ddg = manager.data_dependence_graph
    outgoing_variables: Dict[str, VariableDefinition] = dict()
    for statement in block_statements:
        if statement.statement_type == StatementType.FUNCTION:
            continue
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
        StatementType.OBJECT,
        StatementType.FUNCTION
    }:
        return False
    if statement_1.name != statement_2.name:
        if variable_name is not None:
            return statement_2.name == variable_name
        return True
    if statement_1.ast_node_type in {"update_expression", "+=", "-=", "/=", "*=", "%=", "&=", "|=", "^=", ">>=", "<<="}:
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
        if predecessor in backward_slice:
            continue
        if predecessor.statement_type == StatementType.FUNCTION or "formal_parameter" in predecessor.ast_node_type:
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
        manager: ProgramGraphsManager,
        recursion: bool) -> None:
    for data_successor in manager.data_dependence_graph.successors(variable_def):
        if data_successor.statement_type == StatementType.ASSIGNMENT:
            if data_successor == variable_def or data_successor in forward_slice:
                continue
            if recursion:
                forward_slice.add(data_successor)
                forward_slice.update(set(__obtain_extension(manager, data_successor)))
                __compute_forward_slice_recursive(data_successor, forward_slice, manager, recursion)
            else:
                continue
        else:
            forward_slice.add(data_successor)


def __compute_forward_slice(
        variable_def: VariableDefinition,
        manager: ProgramGraphsManager) -> Set[Statement]:
    forward_slice = set()
    __compute_forward_slice_recursive(
        variable_def,
        forward_slice,
        manager,
        recursion=(variable_def.statement_type in {StatementType.VARIABLE, StatementType.OBJECT}))
    return forward_slice


def __extend_block_singleton(
        block_statements: Set[Statement],
        manager: ProgramGraphsManager) -> SingletonExtensions:
    incoming_variables = __get_incoming_variables(block_statements, manager)
    outgoing_variables = __get_outgoing_variables(block_statements, manager)
    singleton_extensions: SingletonExtensions = list()
    for var_name in set(chain(incoming_variables.keys(), outgoing_variables.keys())):
        new_block = block_statements.copy()
        if var_name in incoming_variables:
            variable_use = incoming_variables[var_name]
            backward_slice = __compute_backward_slice(variable_use, var_name, block_statements, manager)
            new_block.update(backward_slice)
        if var_name in outgoing_variables:
            variable_def = outgoing_variables[var_name]
            forward_slice = __compute_forward_slice(variable_def, manager)
            new_block.update(forward_slice)
        singleton_extensions.append((
            new_block,
            var_name))
    return singleton_extensions


def __filter_anti_dependence(
        new_statements: Set[Statement],
        original_statements: Set[Statement],
        manager: ProgramGraphsManager) -> bool:
    ddg = manager.data_dependence_graph
    if new_statements is None:
        return True
    for statement in new_statements:
        if statement.statement_type == StatementType.FUNCTION:
            continue
        for data_successor in ddg.successors(statement):
            if data_successor in original_statements.union(new_statements):
                continue
            if __flow_dep_given_data_dep(data_successor, statement) and all(
                    (x.statement_type == StatementType.FUNCTION or data_successor not in ddg.successors(x))
                    for x in original_statements):
                return False
    return True


def __filter_control_dependence(
        new_statements: Set[Statement],
        original_statements: Set[Statement],
        manager: ProgramGraphsManager) -> bool:
    cdg = manager.control_dependence_graph
    if new_statements is None or len(new_statements) == 0:
        return True
    missing_cdg_parents = set(reduce(
        lambda x, y: x.union(set(cdg.predecessors(y))),
        {x for x in original_statements if x.statement_type != StatementType.FUNCTION},
        set()))
    all_statements = new_statements.union(original_statements)
    for statement in new_statements:
        if statement.statement_type == StatementType.FUNCTION:
            continue
        for control_successor in cdg.successors(statement):
            if control_successor not in all_statements:
                return False
        for control_predecessor in cdg.predecessors(statement):
            if control_predecessor not in all_statements:
                missing_cdg_parents.add(control_predecessor)

    missing_cdg_parents = missing_cdg_parents.difference(original_statements.union(new_statements))
    missing_cdg_parents = {x for x in missing_cdg_parents if x.statement_type != StatementType.FUNCTION}
    return len(missing_cdg_parents) < 1


def __filter_more_than_one_outgoing(
        slice_candidate: Set[Statement],
        manager: ProgramGraphsManager) -> bool:
    outgoing_variables = __get_outgoing_variables(slice_candidate, manager)
    return len(outgoing_variables.keys()) <= 1


def __filter_valid(
        slice_candidate: Set[Statement],
        manager: ProgramGraphsManager,
        original_statements: Set[Statement] = None) -> bool:
    if original_statements:
        new_statements = slice_candidate.difference(original_statements)
    else:
        new_statements = None
        original_statements = slice_candidate
    if not __filter_anti_dependence(new_statements, original_statements, manager):
        return False
    if not __filter_more_than_one_outgoing(slice_candidate, manager):
        return False
    if not __filter_control_dependence(new_statements, original_statements, manager):
        return False
    return True

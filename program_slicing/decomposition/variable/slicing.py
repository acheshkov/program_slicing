__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/17'

from typing import Set, Dict, Iterator

import networkx

from program_slicing.graph.parse import Lang
from program_slicing.graph.manager import ProgramGraphsManager
from program_slicing.graph.cdg import ControlDependenceGraph
from program_slicing.graph.basic_block import BasicBlock
from program_slicing.graph.statement import Statement, StatementType
from program_slicing.decomposition.program_slice import ProgramSlice
from program_slicing.decomposition.slice_predicate import SlicePredicate


def get_variable_slices(
        source_code: str,
        lang: Lang,
        slice_predicate: SlicePredicate = None,
        include_noneffective: bool = True,
        may_cause_code_duplication: bool = True) -> Iterator[ProgramSlice]:
    """
    For each function and variable in a specified source code generate list of Program Slices.
    :param source_code: source code that should be decomposed.
    :param lang: the source code Lang.
    :param slice_predicate: SlicePredicate object that describes which slices should be filtered. No filtering if None.
    :param include_noneffective: include comments and blank lines to a slice if True.
    :param may_cause_code_duplication: allow to generate slices which extraction will cause code duplication if True.
    :return: generator of the ProgramSlices.
    """
    return get_complete_computation_slices(
        source_code,
        lang,
        slice_predicate=slice_predicate,
        include_noneffective=include_noneffective,
        may_cause_code_duplication=may_cause_code_duplication)


def get_complete_computation_slices(
        source_code: str,
        lang: Lang,
        slice_predicate: SlicePredicate = None,
        include_noneffective: bool = True,
        may_cause_code_duplication: bool = True) -> Iterator[ProgramSlice]:
    """
    For each function and variable in a specified source code generate list of Program Slices.
    :param source_code: source code that should be decomposed.
    :param lang: the source code Lang.
    :param slice_predicate: SlicePredicate object that describes which slices should be filtered. No filtering if None.
    :param include_noneffective: include comments and blank lines to a slice if True.
    :param may_cause_code_duplication: allow to generate slices which extraction will cause code duplication if True.
    :return: generator of the ProgramSlices.
    """
    code_lines = str(source_code).split("\n")
    manager = ProgramGraphsManager(source_code, lang)
    cdg = manager.control_dependence_graph
    function_statements = cdg.entry_points
    for function_statement in function_statements:
        slicing_criteria = __obtain_slicing_criteria(manager, function_statement)
        for variable_statement, seed_statements in slicing_criteria.items():
            complete_computation_slices = __obtain_complete_computation_slices(manager, seed_statements)
            variable_basic_block = manager.get_basic_block(variable_statement)
            if variable_basic_block is None:
                continue
            complete_computation_slice = complete_computation_slices.get(variable_basic_block, [])
            if not complete_computation_slice:
                continue
            if not may_cause_code_duplication:
                affecting_statements = manager.get_affecting_statements(complete_computation_slice)
                if len(manager.get_involved_variables_statements(affecting_statements)) > 1:
                    continue
                if manager.contain_redundant_statements(complete_computation_slice):
                    continue
            if len(manager.get_exit_statements(complete_computation_slice)) > 1:
                continue
            program_slice = ProgramSlice(
                code_lines,
                context=manager if include_noneffective else None
            ).from_statements(complete_computation_slice)
            program_slice.variable = variable_statement
            program_slice.function = function_statement
            if slice_predicate is None or slice_predicate(program_slice, context=manager):
                yield program_slice


def __obtain_variable_statements(cdg: ControlDependenceGraph, root: Statement) -> Set[Statement]:
    return {
        statement for statement in networkx.algorithms.traversal.dfs_tree(cdg, root)
        if statement.statement_type == StatementType.VARIABLE
    }


def __obtain_seed_statements(
        manager: ProgramGraphsManager,
        variable_statement: Statement) -> Set[Statement]:
    ddg = manager.data_dependence_graph
    return {
        statement for statement in networkx.algorithms.traversal.dfs_tree(ddg, variable_statement)
        if __is_slicing_criterion(statement, variable_statement) and manager.get_basic_block(statement) is not None
    }


def __obtain_slicing_criteria(manager: ProgramGraphsManager, root: Statement) -> Dict[Statement, Set[Statement]]:
    variable_statements = __obtain_variable_statements(manager.control_dependence_graph, root)
    return {
        variable_statement: __obtain_seed_statements(manager, variable_statement)
        for variable_statement in variable_statements
    }


def __obtain_common_boundary_blocks(
        manager: ProgramGraphsManager,
        seed_statements: Set[Statement]) -> Set[BasicBlock]:
    result = None
    for seed_statement in seed_statements:
        if result is None:
            result = manager.get_boundary_blocks_for_statement(seed_statement)
        else:
            result.intersection_update(manager.get_boundary_blocks_for_statement(seed_statement))
    return set() if result is None else result


def __obtain_backward_slice(
        manager: ProgramGraphsManager,
        seed_statement: Statement,
        boundary_block: BasicBlock) -> Set[Statement]:
    region = manager.get_reach_blocks(boundary_block)
    result = set()
    __obtain_backward_slice_recursive(manager, seed_statement, region, result)
    return result


def __obtain_backward_slice_recursive(
        manager: ProgramGraphsManager,
        root: Statement,
        region: Set[BasicBlock],
        result: Set[Statement]) -> None:
    if root in result:
        return
    basic_block = manager.get_basic_block(root)
    if basic_block not in region:
        return
    result.add(root)
    for statement in __obtain_necessary_goto(manager, root):
        __obtain_backward_slice_recursive(manager, statement, region, result)
    for statement in __obtain_extension(manager, root, region):
        if statement.statement_type == StatementType.SCOPE:
            result.add(statement)
        else:
            __obtain_backward_slice_recursive(manager, statement, region, result)
    if root in manager.program_dependence_graph:
        for statement in manager.program_dependence_graph.predecessors(root):
            __obtain_backward_slice_recursive(manager, statement, region, result)


def __obtain_complete_computation_slices(
        manager: ProgramGraphsManager,
        seed_statements: Set[Statement]) -> Dict[BasicBlock, Set[Statement]]:
    boundary_blocks = __obtain_common_boundary_blocks(manager, seed_statements)
    complete_computation_slice = {}
    for boundary_block in boundary_blocks:
        backward_slice = set()
        for seed_statement in seed_statements:
            backward_slice.update(__obtain_backward_slice(manager, seed_statement, boundary_block))
        complete_computation_slice[boundary_block] = backward_slice
    return complete_computation_slice


def __obtain_necessary_goto(
        manager: ProgramGraphsManager,
        root: Statement) -> Iterator[Statement]:
    descendants = {statement for statement in networkx.descendants(manager.control_dependence_graph, root)}
    for statement in descendants:
        if __is_necessary_goto(statement, manager, descendants):
            yield statement


def __obtain_branch_extension(
        manager: ProgramGraphsManager,
        root: Statement,
        region: Set[BasicBlock]) -> Iterator[Statement]:
    if root.statement_type == StatementType.BRANCH or root.statement_type == StatementType.LOOP:
        for flow_statement in manager.control_dependence_graph.control_flow[root]:
            if root.start_point <= flow_statement.start_point and root.end_point >= flow_statement.end_point and \
                    flow_statement.statement_type != StatementType.GOTO:
                yield flow_statement
    basic_block = manager.get_basic_block(root)
    block_root = None
    if basic_block is not None:
        for statement in basic_block:
            if __is_branch_container(statement, root):
                yield statement
        block_root = basic_block.root
    if block_root is not None and block_root.statement_type == StatementType.GOTO:
        cdg = manager.control_dependence_graph
        for predecessor in cdg.predecessors(root):
            if predecessor.statement_type == StatementType.BRANCH and (region is None or manager.get_basic_block(predecessor) in region):
                yield block_root
                break


def __obtain_chain_extension(root: Statement, basic_block: BasicBlock) -> Iterator[Statement]:
    return (
        statement for statement in basic_block
        if __is_linear_container(statement, root))


def __obtain_extension(
        manager: ProgramGraphsManager,
        root: Statement,
        region: Set[BasicBlock]) -> Iterator[Statement]:
    for statement in __obtain_branch_extension(manager, root, region):
        yield statement
    basic_block = manager.get_basic_block(root)
    if basic_block is not None:
        for statement in __obtain_chain_extension(root, manager.get_basic_block(root)):
            yield statement
    for statement in __obtain_content(root, basic_block):
        yield statement


def __obtain_content(root: Statement, basic_block: BasicBlock) -> Iterator[Statement]:
    return (
        statement for statement in basic_block
        if __is_linear_container(root, statement) or __is_branch_container(root, statement))


def __is_slicing_criterion(assignment_statement: Statement, variable_statement: Statement) -> bool:
    return \
        (assignment_statement.statement_type == StatementType.VARIABLE or
         assignment_statement.statement_type == StatementType.ASSIGNMENT) and \
        variable_statement.statement_type == StatementType.VARIABLE and \
        variable_statement.name == assignment_statement.name


def __is_necessary_goto(statement: Statement, manager: ProgramGraphsManager, scope_statements: Set[Statement]) -> bool:
    if statement.statement_type == StatementType.EXIT:
        return True
    if statement.statement_type == StatementType.GOTO:
        for flow_statement in manager.control_dependence_graph.control_flow.get(statement, ()):
            if flow_statement not in scope_statements:
                return True
    return False


def __is_linear_container(container: Statement, statement: Statement) -> bool:
    return \
        container.start_point <= statement.start_point and container.end_point >= statement.end_point and \
        container.statement_type != StatementType.BRANCH and \
        container.statement_type != StatementType.LOOP and \
        container.statement_type != StatementType.EXIT and \
        container.statement_type != StatementType.FUNCTION and container != statement


def __is_branch_container(container: Statement, statement: Statement) -> bool:
    return \
        container.start_point <= statement.start_point and container.end_point >= statement.end_point and \
        (container.statement_type == StatementType.BRANCH or
         container.statement_type == StatementType.LOOP) and container != statement

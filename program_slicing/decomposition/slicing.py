__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/17'

import os
from typing import Set, Dict, List, Tuple, Iterator

import networkx

from program_slicing.file_manager import reader
from program_slicing.file_manager import writer
from program_slicing.graph.manager import ProgramGraphsManager
from program_slicing.graph.cdg import ControlDependenceGraph
from program_slicing.graph.basic_block import BasicBlock
from program_slicing.graph.statement import Statement, StatementType
from program_slicing.decomposition.program_slice import ProgramSlice
from program_slicing.decomposition.slice_predicate import SlicePredicate


def decompose_dir(dir_path: str, work_dir: str = None) -> None:
    """
    Decompose all the files in the specified directory and save the result to the work_dir or print it via stdout.
    :param dir_path: path to the source folder with files that should be decomposed.
    :param work_dir: path to the directory where the result will be saved;
    decomposed files will be saved into it with their original names.
    The stdout will be used if work_dir is not specified.
    """
    for file_path in reader.browse_file_sub_paths(dir_path, __get_applicable_formats()):
        decompose_file(file_path, work_dir)


def decompose_file(file_path: str, work_dir: str = None, prefix: str = None) -> None:
    """
    Decompose the specified file and save the result to the work_dir or print it via stdout.
    :param file_path: path to the source file that should be decomposed.
    :param work_dir: path to the directory where the result will be saved;
    decomposed file will be saved into it with it's original name
    and additional suffixes if there will be more than one variants.
    The stdout will be used if work_dir is not specified.
    :param prefix: file_name prefix that should be removed while saving.
    Remove nothing if prefix is None.
    """
    for i, result in enumerate(decompose_code(reader.read_file(file_path), os.path.splitext(file_path)[1])):
        if work_dir is None:
            print(result)
            continue
        if prefix is not None and file_path.startswith(prefix):
            result_path = os.path.join(work_dir, file_path[len(prefix):])
        else:
            result_path = os.path.join(work_dir, os.path.basename(file_path))
        result_path, result_ext = os.path.splitext(result_path)
        result_path = result_path + "." + str(i) + result_ext
        writer.save_file(result_path, result)


def decompose_code(source_code: str, lang: str) -> Iterator[str]:
    """
    Decompose the specified source code and return all the decomposition variants.
    :param source_code: source code that should be decomposed.
    :param lang: string with the source code format described as a file ext (like '.java' or '.xml').
    :return: generator of decomposed source code versions in a string format.
    """
    slice_predicate = SlicePredicate(
        min_amount_of_lines=3,
        max_amount_of_lines=20,
        forbidden_words={"return ", "return;"},
        lang_to_check_parsing=lang,
        has_returnable_variable=True)
    slices = get_complete_computation_slices(source_code, lang, slice_predicate)
    for function_statement, variable_statement, cc_slice in slices:
        yield "\033[33m\nSlice" + \
              ((" of " + function_statement.name) if function_statement.name else "") + \
              " for variable '" + variable_statement.name + \
              "': " + str([a[0].line_number + 1 for a in cc_slice.ranges]) + \
              "\033[00m\n" + cc_slice.code


def get_complete_computation_slices(
        source_code: str,
        lang: str,
        slice_predicate: SlicePredicate = None) -> Iterator[Tuple[Statement, Statement, ProgramSlice]]:
    """
    For each function and variable in a specified source code generate list of Program Slices.
    :param source_code: source code that should be decomposed.
    :param lang: string with the source code format described as a file ext (like '.java' or '.xml').
    :param slice_predicate: SlicePredicate object that describes which slices should be filtered. No filtering if None.
    :return: generator of the function Statement, variable Statement and a corresponding list of slices
    (Statements)
    """
    code_lines = str(source_code).split("\n")
    manager = ProgramGraphsManager(source_code, lang)
    cdg = manager.get_control_dependence_graph()
    function_statements = cdg.entry_points
    for function_statement in function_statements:
        slicing_criteria = __obtain_slicing_criteria(manager, function_statement)
        for variable_statement, seed_statements in slicing_criteria.items():
            complete_computation_slices = __obtain_complete_computation_slices(manager, seed_statements)
            variable_basic_block = manager.get_basic_block(variable_statement)
            if variable_basic_block is None:
                continue
            complete_computation_slice = complete_computation_slices.get(variable_basic_block, [])
            if complete_computation_slice:
                program_slice = ProgramSlice(code_lines).from_statements(complete_computation_slice)
                if slice_predicate is None or slice_predicate(program_slice):
                    yield function_statement, variable_statement, program_slice


def __obtain_variable_statements(cdg: ControlDependenceGraph, root: Statement) -> Set[Statement]:
    return {
        statement for statement in networkx.algorithms.traversal.dfs_tree(cdg, root)
        if statement.statement_type == StatementType.VARIABLE
    }


def __obtain_seed_statements(
        manager: ProgramGraphsManager,
        variable_statement: Statement) -> Set[Statement]:
    ddg = manager.get_data_dependence_graph()
    return {
        statement for statement in networkx.algorithms.traversal.dfs_tree(ddg, variable_statement)
        if __is_slicing_criterion(statement, variable_statement) and manager.get_basic_block(statement) is not None
    }


def __obtain_slicing_criteria(manager: ProgramGraphsManager, root: Statement) -> Dict[Statement, Set[Statement]]:
    variable_statements = __obtain_variable_statements(manager.get_control_dependence_graph(), root)
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
    for statement in __obtain_content(root, basic_block):
        result.add(statement)
    if root in manager.get_program_dependence_graph():
        for statement in manager.get_program_dependence_graph().predecessors(root):
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
    descendants = {statement for statement in networkx.descendants(manager.get_control_dependence_graph(), root)}
    for statement in descendants:
        if __is_necessary_goto(statement, manager, descendants):
            yield statement


def __obtain_branch_extension(
        manager: ProgramGraphsManager,
        root: Statement,
        region: Set[BasicBlock]) -> Iterator[Statement]:
    if root.statement_type == StatementType.BRANCH or root.statement_type == StatementType.LOOP:
        for flow_statement in manager.get_control_dependence_graph().control_flow[root]:
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
        cdg = manager.get_control_dependence_graph()
        for predecessor in cdg.predecessors(root):
            if predecessor.statement_type == StatementType.BRANCH and manager.get_basic_block(predecessor) in region:
                yield block_root
                break


def __obtain_linear_extension(root: Statement, basic_block: BasicBlock) -> Iterator[Statement]:
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
        for statement in __obtain_linear_extension(root, manager.get_basic_block(root)):
            yield statement


def __obtain_content(root: Statement, basic_block: BasicBlock) -> Iterator[Statement]:
    return (
        statement for statement in basic_block
        if __is_linear_container(root, statement))


def __is_slicing_criterion(assignment_statement: Statement, variable_statement: Statement) -> bool:
    return \
        (assignment_statement.statement_type == StatementType.VARIABLE or
         assignment_statement.statement_type == StatementType.ASSIGNMENT) and \
        variable_statement.statement_type == StatementType.VARIABLE and \
        variable_statement.name == assignment_statement.name


def __is_necessary_goto(statement: Statement, manager: ProgramGraphsManager, scope_statements: Set[Statement]) -> bool:
    if statement.statement_type == StatementType.GOTO:
        for flow_statement in manager.get_control_dependence_graph().control_flow.get(statement, ()):
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


def __get_applicable_formats() -> List[str]:
    """
    Get the list of file formats that are supported by parsers.
    :return: list of strings like '.java' or '.xml'
    """
    return [".java"]

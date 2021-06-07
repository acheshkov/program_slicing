__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/17'

import os
from typing import Set, Dict, List, Tuple, Generator

import networkx

from program_slicing.file_manager import reader
from program_slicing.file_manager import writer
from program_slicing.graph.manager import ProgramGraphsManager
from program_slicing.graph.cdg import ControlDependenceGraph
from program_slicing.graph.basic_block import BasicBlock
from program_slicing.graph.statement import Statement, StatementType
from program_slicing.decomposition.code_lines_slicer import CodeLinesSlicer
from program_slicing import utils


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


def decompose_code(source_code: str, lang: str) -> Generator[str, None, None]:
    """
    Decompose the specified source code and return all the decomposition variants.
    :param source_code: source code that should be decomposed.
    :param lang: string with the source code format described as a file ext (like '.java' or '.xml').
    :return: generator of decomposed source code versions in a string format.
    """
    for function_statement, variable_statement, cc_slice in \
            utils.filter_slices(get_complete_computation_slices(source_code, lang))\
            .by_min_amount_of_lines(5)\
            .by_max_amount_of_lines(15):
        yield "\033[33m\nSlice" + \
              ((" of " + function_statement.name) if function_statement.name is not None else "") + \
              " for variable '" + variable_statement.name + \
              "':\033[00m\n" + cc_slice.get_slice_code()


def get_complete_computation_slices(
        source_code: str,
        lang: str) -> Generator[Tuple[Statement, Statement, CodeLinesSlicer], None, None]:
    """
    For each function and variable in a specified source code generate list of slices.
    Slice is a list of position ranges.
    :param source_code: source code that should be decomposed.
    :param lang: string with the source code format described as a file ext (like '.java' or '.xml').
    :return: generator of the function Statement, variable Statement and a corresponding list of slices
    (CodeLinesSlicer)
    """
    code_lines = str(source_code).split("\n")
    for function_statement, variable_statement, complete_computation_slice in \
            get_complete_computation_slices_statements(source_code, lang):
        code_lines_slicer = CodeLinesSlicer(code_lines)
        for statement in complete_computation_slice:
            code_lines_slicer.add_statement(statement)
        yield function_statement, variable_statement, code_lines_slicer


def get_complete_computation_slices_statements(
        source_code: str,
        lang: str) -> Generator[Tuple[Statement, Statement, List[Statement]], None, None]:
    """
    For each function and variable in a specified source code generate list of slices.
    Slice is a list of Statements.
    :param source_code: source code that should be decomposed.
    :param lang: string with the source code format described as a file ext (like '.java' or '.xml').
    :return: generator of the function Statement, variable Statement and a corresponding list of slices
    (Statements)
    """
    manager = ProgramGraphsManager(source_code, lang)
    cdg = manager.cdg
    function_statements = cdg.get_entry_points()
    for function_statement in function_statements:
        slicing_criteria = __obtain_slicing_criteria(cdg, function_statement)
        for variable_statement, seed_statements in slicing_criteria.items():
            complete_computation_slices = __obtain_complete_computation_slices(manager, seed_statements)
            variable_basic_block = manager.get_basic_block(variable_statement)
            if variable_basic_block is None:
                continue
            complete_computation_slice = complete_computation_slices.get(variable_basic_block, [])
            if complete_computation_slice:
                yield function_statement, variable_statement, complete_computation_slice


def __obtain_variable_statements(cdg: ControlDependenceGraph, root: Statement) -> Set[Statement]:
    return {
        statement for statement in networkx.algorithms.traversal.dfs_tree(cdg, root)
        if statement.statement_type == StatementType.VARIABLE
    }


def __obtain_seed_statements(
        cdg: ControlDependenceGraph,
        root: Statement,
        variable_statement: Statement) -> Set[Statement]:
    return {
        statement for statement in networkx.algorithms.traversal.dfs_tree(cdg, root)
        if __is_slicing_criterion(statement, variable_statement)
    }


def __obtain_slicing_criteria(cdg: ControlDependenceGraph, root: Statement) -> Dict[Statement, Set[Statement]]:
    variable_statements = __obtain_variable_statements(cdg, root)
    return {
        variable_statement: __obtain_seed_statements(cdg, root, variable_statement)
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
    return result


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
        result: Set[Statement]):
    if root in result:
        return
    basic_block = manager.get_basic_block(root)
    if basic_block not in region:
        return
    result.add(root)
    for statement in basic_block.get_statements():
        if statement.start_point[0] >= root.start_point[0] and statement.end_point[0] <= root.end_point[0]:
            result.add(statement)
            if statement in manager.ddg:
                for predecessor in manager.ddg.predecessors(statement):
                    __obtain_backward_slice_recursive(manager, predecessor, region, result)
        elif statement.start_point[0] <= root.start_point[0] and statement.end_point[0] >= root.end_point[0] and (
                statement.statement_type == StatementType.UNKNOWN or
                statement.statement_type == StatementType.SCOPE):
            result.add(statement)
    if root in manager.pdg:
        for statement in manager.pdg.predecessors(root):
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


def __is_slicing_criterion(assignment_statement: Statement, variable_statement: Statement) -> bool:
    return \
        (assignment_statement.statement_type == StatementType.VARIABLE or
         assignment_statement.statement_type == StatementType.ASSIGNMENT) and \
        variable_statement.statement_type == StatementType.VARIABLE and \
        variable_statement.name == assignment_statement.name


def __get_applicable_formats() -> List[str]:
    """
    Get the list of file formats that are supported by parsers.
    :return: list of strings like '.java' or '.xml'
    """
    return [".java"]

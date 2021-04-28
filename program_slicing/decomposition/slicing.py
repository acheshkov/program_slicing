__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/17'

import os
from typing import Set, Dict, List, Generator

import networkx

from program_slicing.file_manager import reader
from program_slicing.file_manager import writer
from program_slicing.graph.manager import ProgramGraphsManager
from program_slicing.graph.cdg import ControlDependenceGraph
from program_slicing.graph.basic_block import BasicBlock
from program_slicing.graph.statement import Statement, \
    STATEMENT_TYPE_VARIABLE, \
    STATEMENT_TYPE_ASSIGNMENT


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
    :param lang: source code format like '.java' or '.xml'.
    :return: generator of decomposed source code versions in a string format.
    """
    manager = ProgramGraphsManager(source_code, lang)
    cdg = manager.cdg
    function_statements = cdg.get_entry_points()
    for function_statement in function_statements:
        slicing_criteria = __obtain_slicing_criteria(cdg, function_statement)
        for variable_statement, seed_statements in slicing_criteria.items():
            common_boundary_blocks = __obtain_common_boundary_blocks(manager, seed_statements)
            yield str((variable_statement, common_boundary_blocks))


def __obtain_variable_statements(cdg: ControlDependenceGraph, root: Statement) -> Set[Statement]:
    return {
        statement for statement in networkx.algorithms.traversal.dfs_tree(cdg, root)
        if statement.statement_type == STATEMENT_TYPE_VARIABLE
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


def __obtain_backward_slice(manager: ProgramGraphsManager, slicing_criterion, boundary_block):
    pass


def __is_slicing_criterion(assignment_statement: Statement, variable_statement: Statement) -> bool:
    return \
        assignment_statement.statement_type == STATEMENT_TYPE_ASSIGNMENT and \
        variable_statement.statement_type == STATEMENT_TYPE_VARIABLE and \
        variable_statement.name == assignment_statement.name


def __get_applicable_formats() -> List[str]:
    """
    Get the list of file formats that are supported by parsers.
    :return: list of strings like '.java' or '.xml'
    """
    return [".java"]

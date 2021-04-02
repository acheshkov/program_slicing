__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/17'

from typing import List, Generator

import os
import networkx
from typing import Set, Dict
from program_slicing.file_manager import reader
from program_slicing.file_manager import writer
from program_slicing.graph.manager import ProgramGraphsManager
from program_slicing.graph.cdg import ControlDependenceGraph
from program_slicing.graph.cdg_content import CDGContent, \
    CDG_CONTENT_TYPE_VARIABLE, \
    CDG_CONTENT_TYPE_ASSIGNMENT


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
    :return: generator of decomposed versions.
    """
    manager = ProgramGraphsManager((source_code, lang))
    cdg = manager.cdg
    cfg = manager.cfg
    function_nodes = cdg.get_roots()
    for function_node in function_nodes:
        slicing_criteria = __obtain_slicing_criteria(cdg, function_node)
        print(slicing_criteria)
    print(cfg)
    return (str(i) for i in range(1))


def __obtain_variable_nodes(cdg: ControlDependenceGraph, root: CDGContent) -> Set[CDGContent]:
    return {
        node for node in networkx.algorithms.traversal.dfs_tree(cdg, root)
        if node.content_type == CDG_CONTENT_TYPE_VARIABLE
    }


def __obtain_seed_statement_nodes(
        cdg: ControlDependenceGraph,
        root: CDGContent,
        variable_node: CDGContent) -> Set[CDGContent]:
    return {
        node for node in networkx.algorithms.traversal.dfs_tree(cdg, root)
        if __is_slicing_criteria(node, variable_node)
    }


def __obtain_slicing_criteria(cdg: ControlDependenceGraph, root: CDGContent) -> Dict[CDGContent, Set[CDGContent]]:
    variable_nodes = __obtain_variable_nodes(cdg, root)
    return {
        variable_node: __obtain_seed_statement_nodes(cdg, root, variable_node) for variable_node in variable_nodes}


def __is_slicing_criteria(assignment_node: CDGContent, variable_node: CDGContent) -> bool:
    return \
        assignment_node.content_type == CDG_CONTENT_TYPE_ASSIGNMENT and \
        variable_node.content_type == CDG_CONTENT_TYPE_VARIABLE and \
        variable_node.name == assignment_node.name


def __get_applicable_formats() -> List[str]:
    """
    Get the list of file formats that can be used in data generating or pattern mining tasks.
    :return: list of strings like '.java' or '.xml'
    """
    return [".java"]

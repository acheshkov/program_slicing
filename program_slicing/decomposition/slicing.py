__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/17'

import os
from typing import List, Iterator

from program_slicing.file_manager import reader
from program_slicing.file_manager import writer
from program_slicing.decomposition.slice_predicate import SlicePredicate
from program_slicing.decomposition.block.slicing import get_block_slices
from program_slicing.decomposition.variable.slicing import get_variable_slices


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
        min_amount_of_statements=3,
        max_amount_of_statements=60,
        min_amount_of_lines=3,
        max_amount_of_lines=40,
        lang_to_check_parsing=lang,
        has_returnable_variable=True)
    variable_slices = get_variable_slices(source_code, lang, slice_predicate)
    for program_slice in variable_slices:
        yield "\033[33m\nVariable slice" + \
              ((" of " + program_slice.function.name) if program_slice.function.name else "") + \
              " for variable '" + program_slice.variable.name + \
              "': " + str([a[0].line_number + 1 for a in program_slice.ranges]) + \
              "\033[00m\n" + program_slice.code

    block_slices = get_block_slices(source_code, lang, slice_predicate)
    for program_slice in block_slices:
        yield "\033[33m\nBlock slice: " + str([a[0].line_number + 1 for a in program_slice.ranges]) + \
              "\033[00m\n" + program_slice.code


def __get_applicable_formats() -> List[str]:
    """
    Get the list of file formats that are supported by parsers.
    :return: list of strings like '.java' or '.xml'
    """
    return [".java"]

__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/23'

from program_slicing.parse import cg_java
from program_slicing.parse import cfg_java
from program_slicing.parse import cdg_java
from program_slicing.parse.cg import ControlGraph
from program_slicing.parse.cfg import ControlFlowGraph
from program_slicing.parse.cdg import ControlDependencyGraph

FILE_EXT_JAVA = ".java"


def control_graph(source_code: str, file_ext: str) -> ControlGraph:
    """
    Parse the source code in a specified format into a Control Graph that contains Control Dependence and Control Flow.
    :param source_code: string with the source code in it.
    :param file_ext: string with the source code format described as a file ext (like '.java' or '.xml').
    :return: Control Graph.
    """
    if file_ext == FILE_EXT_JAVA:
        return cg_java.parse(source_code)


def control_flow_graph(source_code: str, file_ext: str) -> ControlFlowGraph:
    """
    Parse the source code in a specified format into a Control Flow Graph .
    :param source_code: string with the source code in it.
    :param file_ext: string with the source code format described as a file ext (like '.java' or '.xml').
    :return: Control Flow Graph.
    """
    if file_ext == FILE_EXT_JAVA:
        return cfg_java.parse(source_code)


def control_dependency_graph(source_code: str, file_ext: str) -> ControlDependencyGraph:
    """
    Parse the source code in a specified format into a Control Dependency Graph.
    :param source_code: string with the source code in it.
    :param file_ext: string with the source code format described as a file ext (like '.java' or '.xml')
    :return: Control Dependency Graph.
    """
    if file_ext == FILE_EXT_JAVA:
        return cdg_java.parse(source_code)

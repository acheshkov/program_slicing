__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/23'

from program_slicing.graph.parse import cdg_java, cfg_java
from program_slicing.graph.cfg import ControlFlowGraph
from program_slicing.graph.cdg import ControlDependenceGraph

FILE_EXT_JAVA = ".java"


def control_flow_graph(source_code: str, file_ext: str) -> ControlFlowGraph:
    """
    Parse the source code in a specified format into a Control Flow Graph .
    :param source_code: string with the source code in it.
    :param file_ext: string with the source code format described as a file ext (like '.java' or '.xml').
    :return: Control Flow Graph.
    """
    if file_ext == FILE_EXT_JAVA:
        return cfg_java.parse(source_code)


def control_dependence_graph(source_code: str, file_ext: str) -> ControlDependenceGraph:
    """
    Parse the source code in a specified format into a Control Dependence Graph.
    :param source_code: string with the source code in it.
    :param file_ext: string with the source code format described as a file ext (like '.java' or '.xml')
    :return: Control Dependence Graph.
    """
    if file_ext == FILE_EXT_JAVA:
        return cdg_java.parse(source_code)

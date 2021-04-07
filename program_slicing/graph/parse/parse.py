__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/23'

from program_slicing.graph.parse import cdg_java
from program_slicing.graph.parse import cfg_java
from program_slicing.graph.cfg import ControlFlowGraph
from program_slicing.graph.cdg import ControlDependenceGraph

LANG_JAVA = ".java"


def control_flow_graph(source_code: str, lang: str) -> ControlFlowGraph:
    """
    Parse the source code in a specified format into a Control Flow Graph .
    :param source_code: string with the source code in it.
    :param lang: string with the source code format described as a file ext (like '.java' or '.xml').
    :return: Control Flow Graph.
    """
    if lang == LANG_JAVA:
        return cfg_java.parse(source_code)


def control_dependence_graph(source_code: str, lang: str) -> ControlDependenceGraph:
    """
    Parse the source code in a specified format into a Control Dependence Graph.
    :param source_code: string with the source code in it.
    :param lang: string with the source code format described as a file ext (like '.java' or '.xml')
    :return: Control Dependence Graph.
    """
    if lang == LANG_JAVA:
        return cdg_java.parse(source_code)

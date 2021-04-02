__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/30'

from program_slicing.graph.cfg import ControlFlowGraph
from program_slicing.graph.parse import cdg_java
from program_slicing.graph.convert.cdg import to_cfg


def parse(source_code: str) -> ControlFlowGraph:
    """
    Parse the source code string into a Control Flow Graph.
    :param source_code: the string that should to be parsed.
    :return: Control Flow Graph
    """
    return to_cfg(cdg_java.parse(source_code))

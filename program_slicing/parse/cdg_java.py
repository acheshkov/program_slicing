__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/30'

from program_slicing.parse.cdg import ControlDependencyGraph
from program_slicing.parse import cg_java


def parse(source_code: str) -> ControlDependencyGraph:
    """
    Parse the source code string into a Control Dependency Graph.
    :param source_code: the string that should to be parsed.
    :return: Control Dependency Graph
    """
    return ControlDependencyGraph(cg_java.parse(source_code))

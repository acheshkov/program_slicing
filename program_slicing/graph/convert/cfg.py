__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/04/01'

from program_slicing.graph.cdg import ControlDependenceGraph
from program_slicing.graph.cfg import ControlFlowGraph


def to_cdg(cdg: ControlFlowGraph) -> ControlDependenceGraph:
    """
    Convert the Control Flow Graph into a Control Dependence Graph.
    Any changes in the original graph after converting will affect the converted one.
    :param cdg: Control Flow Graph that should to be converted.
    :return: Control Dependence Graph
    """
    return ControlDependenceGraph()

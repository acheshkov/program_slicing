__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/04/20'

from program_slicing.graph.cdg import ControlDependenceGraph
from program_slicing.graph.cfg import ControlFlowGraph
from program_slicing.graph.ddg import DataDependenceGraph


def to_cdg(ddg: DataDependenceGraph) -> ControlDependenceGraph:
    """
    Convert the Data Dependence Graph into a Control Dependence Graph.
    New graph will contain nodes, links on which where listed in the original one so that
    any changes made after converting in the original graph's content will affect the converted one.
    :param ddg: Data Dependence Graph that should to be converted.
    :return: Control Dependence Graph which nodes where contained in the Data Dependence Graph on which it was based on.
    """
    raise NotImplementedError()


def to_cfg(ddg: DataDependenceGraph) -> ControlFlowGraph:
    """
    Convert the Data Dependence Graph into a Control Flow Graph.
    New graph will contain same nodes as in the original one so that
    any changes made after converting in the original graph's content will affect the converted one.
    :param ddg: Data Dependence Graph that should to be converted.
    :return: Control Flow Graph which nodes where presented in the Data Dependence Graph on which it was based on.
    """
    raise NotImplementedError()

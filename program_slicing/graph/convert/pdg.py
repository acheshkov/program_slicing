__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/04/22'

from program_slicing.graph.cdg import ControlDependenceGraph
from program_slicing.graph.cfg import ControlFlowGraph
from program_slicing.graph.ddg import DataDependenceGraph
from program_slicing.graph.pdg import ProgramDependenceGraph


def to_cdg(pdg: ProgramDependenceGraph) -> ControlDependenceGraph:
    """
    Convert the Program Dependence Graph into a Control Dependence Graph.
    New graph will contain nodes, links on which where listed in the original one so that
    any changes made after converting in the original graph's statements will affect the converted one.
    :param pdg: Program Dependence Graph that should to be converted.
    :return: Control Dependence Graph which nodes where contained in the original Program Dependence Graph.
    """
    raise NotImplementedError()


def to_cfg(pdg: ProgramDependenceGraph) -> ControlFlowGraph:
    """
    Convert the Program Dependence Graph into a Control Flow Graph.
    New graph will contain same nodes as in the original one so that
    any changes made after converting in the original graph's statements will affect the converted one.
    :param pdg: Program Dependence Graph that should to be converted.
    :return: Control Flow Graph which nodes where presented in the Program Dependence Graph on which it was based on.
    """
    raise NotImplementedError()


def to_ddg(pdg: ProgramDependenceGraph) -> DataDependenceGraph:
    """
    Convert the Program Dependence Graph into a Data Dependence Graph.
    New graph will contain same nodes as in the original one so that
    any changes made after converting in the original graph's statements will affect the converted one.
    :param pdg: Program Dependence Graph that should to be converted.
    :return: Data Dependence Graph which nodes where presented in the Program Dependence Graph on which it was based on.
    """
    raise NotImplementedError()

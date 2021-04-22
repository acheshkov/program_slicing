__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/04/20'

from program_slicing.graph.pdg import ProgramDependenceGraph
from program_slicing.graph.parse import cdg_java
from program_slicing.graph import convert


def parse(source_code: str) -> ProgramDependenceGraph:
    """
    Parse the source code string into a Data Dependence Graph.
    :param source_code: the string that should to be parsed.
    :return: Data Dependence Graph
    """
    return convert.cdg.to_pdg(cdg_java.parse(source_code))

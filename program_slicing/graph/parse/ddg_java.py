__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/04/20'

from program_slicing.graph.ddg import DataDependenceGraph
from program_slicing.graph.parse import cdg_java
from program_slicing.graph import convert


def parse(source_code: str) -> DataDependenceGraph:
    """
    Parse the source code string into a Data Dependence Graph.
    :param source_code: the string that should to be parsed.
    :return: Data Dependence Graph
    """
    return convert.cdg.to_ddg(cdg_java.parse(source_code))

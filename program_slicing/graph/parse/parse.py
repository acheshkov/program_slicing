__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/23'

from enum import Enum

from tree_sitter import Tree

from program_slicing.graph.parse import tree_sitter_ast_java
from program_slicing.graph.parse import cdg_java
from program_slicing.graph.parse import cfg_java
from program_slicing.graph.parse import ddg_java
from program_slicing.graph.parse import pdg_java
from program_slicing.graph.cfg import ControlFlowGraph
from program_slicing.graph.cdg import ControlDependenceGraph
from program_slicing.graph.ddg import DataDependenceGraph
from program_slicing.graph.pdg import ProgramDependenceGraph


class Lang(Enum):
    JAVA = ".java"
    XML = ".xml"


def tree_sitter_ast(source_code: str, lang: Lang) -> Tree:
    """
    Parse the source code in a specified format into a Tree Sitter AST.
    :param source_code: string with the source code in it.
    :param lang: the source code Lang.
    :return: Tree Sitter AST.
    """
    if lang == Lang.JAVA:
        return tree_sitter_ast_java.parse(source_code)
    else:
        raise NotImplementedError()


def control_flow_graph(source_code: str, lang: Lang) -> ControlFlowGraph:
    """
    Parse the source code in a specified format into a Control Flow Graph.
    :param source_code: string with the source code in it.
    :param lang: the source code Lang.
    :return: Control Flow Graph.
    """
    if lang == Lang.JAVA:
        return cfg_java.parse(source_code)
    else:
        raise NotImplementedError()


def control_dependence_graph(source_code: str, lang: Lang) -> ControlDependenceGraph:
    """
    Parse the source code in a specified format into a Control Dependence Graph.
    :param source_code: string with the source code in it.
    :param lang: the source code Lang.
    :return: Control Dependence Graph.
    """
    if lang == Lang.JAVA:
        return cdg_java.parse(source_code)
    else:
        raise NotImplementedError()


def data_dependence_graph(source_code: str, lang: Lang) -> DataDependenceGraph:
    """
    Parse the source code in a specified format into a Data Dependence Graph.
    :param source_code: string with the source code in it.
    :param lang: the source code Lang.
    :return: Data Dependence Graph.
    """
    if lang == Lang.JAVA:
        return ddg_java.parse(source_code)
    else:
        raise NotImplementedError()


def program_dependence_graph(source_code: str, lang: Lang) -> ProgramDependenceGraph:
    """
    Parse the source code in a specified format into a Program Dependence Graph.
    :param source_code: string with the source code in it.
    :param lang: the source code Lang.
    :return: Program Dependence Graph.
    """
    if lang == Lang.JAVA:
        return pdg_java.parse(source_code)
    else:
        raise NotImplementedError()

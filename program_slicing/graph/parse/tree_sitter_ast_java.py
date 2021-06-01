__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/30'

from tree_sitter import Tree

from program_slicing.graph.parse import tree_sitter_parsers


def parse(source_code: str) -> Tree:
    """
    Parse the source code string into a Tree Sitter AST.
    :param source_code: string with the source code in it.
    :return: Tree Sitter AST.
    """
    return tree_sitter_parsers.java().parse(bytes(source_code, "utf8"))

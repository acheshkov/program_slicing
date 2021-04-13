__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/30'

from typing import List, Tuple

from tree_sitter import Node

from program_slicing.graph.parse import tree_sitter_parsers
from program_slicing.graph.cdg import ControlDependenceGraph
from program_slicing.graph.cdg_node import CDGNode, \
    CDG_NODE_TYPE_FUNCTION, \
    CDG_NODE_TYPE_VARIABLE, \
    CDG_NODE_TYPE_ASSIGNMENT, \
    CDG_NODE_TYPE_CALL, \
    CDG_NODE_TYPE_STATEMENTS, \
    CDG_NODE_TYPE_BRANCH, \
    CDG_NODE_TYPE_LOOP, \
    CDG_NODE_TYPE_BREAK, \
    CDG_NODE_TYPE_GOTO, \
    CDG_NODE_TYPE_OBJECT, \
    CDG_NODE_TYPE_EXIT


parser = tree_sitter_parsers.java()
node_type_map = {
    "variable_definition":
        CDG_NODE_TYPE_VARIABLE,
    "function_definition":
        CDG_NODE_TYPE_FUNCTION,
    "if":
        CDG_NODE_TYPE_BRANCH,
    "try":
        CDG_NODE_TYPE_BRANCH,
    "while":
        CDG_NODE_TYPE_LOOP,
    "for":
        CDG_NODE_TYPE_LOOP,
    "assign":
        CDG_NODE_TYPE_ASSIGNMENT,
    "call":
        CDG_NODE_TYPE_CALL,
    "block":
        CDG_NODE_TYPE_STATEMENTS,
    "continue":
        CDG_NODE_TYPE_GOTO,
    "break":
        CDG_NODE_TYPE_BREAK,
    "return":
        CDG_NODE_TYPE_EXIT
}


def parse(source_code: str) -> ControlDependenceGraph:
    """
    Parse the source code string into a Control Dependence Graph.
    :param source_code: the string that should to be parsed.
    :return: Control Dependence Graph
    """
    ast = parser.parse(bytes(source_code, "utf8"))
    result = ControlDependenceGraph()
    __parse(ast.root_node, result)
    return result


def __parse(ast: Node, cdg: ControlDependenceGraph) -> CDGNode:
    """
    Parse the javalang ast into a Control Dependence Graph.
    :param ast: javalang node
    :param cdg: Control Dependence Graph that will contain
    :return: parsed node.
    """
    children = []
    for child in ast.children:
        if issubclass(type(child), Node):
            children.append(__parse(child, cdg))
        elif type(child) is list or type(child) is set:
            for sub_child in child:
                if issubclass(type(sub_child), Node):
                    children.append(__parse(sub_child, cdg))
    node_type = __parse_node_type(ast)
    line_range = __parse_line_range(ast, children)
    node = CDGNode(
        str(ast.__class__),
        node_type,
        line_range,
        name=__parse_node_name(ast))
    cdg.add_node(node)
    for child in children:
        cdg.add_edge(node, child)
    if node_type == CDG_NODE_TYPE_FUNCTION:
        cdg.add_entry_point(node)
    return node


def __parse_node_type(ast: Node) -> str:
    return node_type_map.get(type(ast), CDG_NODE_TYPE_OBJECT)


def __parse_line_range(ast: Node, children: List[CDGNode]) -> Tuple[int, int]:
    return (
        (children[0].line_range[0] if children else -1) if ast.start_point is None else ast.start_point,
        (children[-1].line_range[1] if children else -1) if ast.end_point is None else ast.end_point)


def __parse_node_name(ast: Node) -> str:
    name = getattr(ast, 'name', None)
    if name is not None:
        return str(name)

    node_type = __parse_node_type(ast)
    if node_type == CDG_NODE_TYPE_ASSIGNMENT:
        name = ast.children[0].member

    return name

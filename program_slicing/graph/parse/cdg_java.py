__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/30'

import javalang
from typing import List, Tuple

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


node_type_map = {
    javalang.parser.tree.VariableDeclaration:
        CDG_NODE_TYPE_VARIABLE,
    javalang.parser.tree.LocalVariableDeclaration:
        CDG_NODE_TYPE_VARIABLE,
    javalang.parser.tree.MethodDeclaration:
        CDG_NODE_TYPE_FUNCTION,
    javalang.parser.tree.IfStatement:
        CDG_NODE_TYPE_BRANCH,
    javalang.parser.tree.TryStatement:
        CDG_NODE_TYPE_BRANCH,
    javalang.parser.tree.WhileStatement:
        CDG_NODE_TYPE_LOOP,
    javalang.parser.tree.ForStatement:
        CDG_NODE_TYPE_LOOP,
    javalang.parser.tree.Assignment:
        CDG_NODE_TYPE_ASSIGNMENT,
    javalang.parser.tree.MethodInvocation:
        CDG_NODE_TYPE_CALL,
    javalang.parser.tree.BlockStatement:
        CDG_NODE_TYPE_STATEMENTS,
    javalang.parser.tree.ContinueStatement:
        CDG_NODE_TYPE_GOTO,
    javalang.parser.tree.BreakStatement:
        CDG_NODE_TYPE_BREAK,
    javalang.parser.tree.ReturnStatement:
        CDG_NODE_TYPE_EXIT
}


def parse(source_code: str) -> ControlDependenceGraph:
    """
    Parse the source code string into a Control Dependence Graph.
    :param source_code: the string that should to be parsed.
    :return: Control Dependence Graph
    """
    ast = javalang.parse.parse(source_code)
    result = ControlDependenceGraph()
    __parse(ast, result)
    return result


def __parse(ast: javalang.parser.tree.Node, cdg: ControlDependenceGraph) -> CDGNode:
    """
    Parse the javalang ast into a Control Dependence Graph.
    :param ast: javalang node
    :param cdg: Control Dependence Graph that will contain
    :return: parsed node.
    """
    children = []
    for child in ast.children:
        if issubclass(type(child), javalang.parser.tree.Node):
            children.append(__parse(child, cdg))
        elif type(child) is list or type(child) is set:
            for sub_child in child:
                if issubclass(type(sub_child), javalang.parser.tree.Node):
                    children.append(__parse(sub_child, cdg))
    node_type = __parse_node_type(ast)
    line_range = __parse_line_range(ast, children)
    node = CDGNode(
        str(ast.__class__),
        node_type,
        line_range,
        name=str(getattr(ast, 'name', None)))
    cdg.add_node(node)
    for child in children:
        cdg.add_edge(node, child)
    if node_type == CDG_NODE_TYPE_FUNCTION:
        cdg.add_entry_point(node)
    return node


def __parse_node_type(ast: javalang.parser.tree.Node) -> str:
    return node_type_map.get(type(ast), CDG_NODE_TYPE_OBJECT)


def __parse_line_range(ast: javalang.parser.tree.Node, children: List[CDGNode]) -> Tuple[int, int]:
    return (
        (children[0].line_range[0] if children else -1) if ast.position is None else ast.position[0],
        children[-1].line_range[1] if children else (-1 if ast.position is None else ast.position[0]))

__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/30'

import javalang
from typing import List, Tuple
from program_slicing.graph.cdg import ControlDependenceGraph
from program_slicing.graph.cdg_content import CDGContent, \
    CDG_CONTENT_TYPE_FUNCTION, \
    CDG_CONTENT_TYPE_VARIABLE, \
    CDG_CONTENT_TYPE_ASSIGNMENT, \
    CDG_CONTENT_TYPE_CALL, \
    CDG_CONTENT_TYPE_STATEMENTS, \
    CDG_CONTENT_TYPE_BRANCH, \
    CDG_CONTENT_TYPE_LOOP, \
    CDG_CONTENT_TYPE_BREAK, \
    CDG_CONTENT_TYPE_GOTO, \
    CDG_CONTENT_TYPE_OBJECT, \
    CDG_CONTENT_TYPE_EXIT


content_type_map = {
    javalang.parser.tree.VariableDeclaration:
        CDG_CONTENT_TYPE_VARIABLE,
    javalang.parser.tree.LocalVariableDeclaration:
        CDG_CONTENT_TYPE_VARIABLE,
    javalang.parser.tree.MethodDeclaration:
        CDG_CONTENT_TYPE_FUNCTION,
    javalang.parser.tree.IfStatement:
        CDG_CONTENT_TYPE_BRANCH,
    javalang.parser.tree.TryStatement:
        CDG_CONTENT_TYPE_BRANCH,
    javalang.parser.tree.WhileStatement:
        CDG_CONTENT_TYPE_LOOP,
    javalang.parser.tree.ForStatement:
        CDG_CONTENT_TYPE_LOOP,
    javalang.parser.tree.Assignment:
        CDG_CONTENT_TYPE_ASSIGNMENT,
    javalang.parser.tree.MethodInvocation:
        CDG_CONTENT_TYPE_CALL,
    javalang.parser.tree.BlockStatement:
        CDG_CONTENT_TYPE_STATEMENTS,
    javalang.parser.tree.ContinueStatement:
        CDG_CONTENT_TYPE_GOTO,
    javalang.parser.tree.BreakStatement:
        CDG_CONTENT_TYPE_BREAK,
    javalang.parser.tree.ReturnStatement:
        CDG_CONTENT_TYPE_EXIT
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


def __parse(ast: javalang.parser.tree.Node, cdg: ControlDependenceGraph) -> CDGContent:
    """
    Parse the javalang ast into a Control Dependence Graph.
    :param ast: javalang node
    :param cdg: Control Dependence Graph that will contain
    :return: parsed node content.
    """
    children = []
    for child in ast.children:
        if issubclass(type(child), javalang.parser.tree.Node):
            children.append(__parse(child, cdg))
        elif type(child) is list or type(child) is set:
            for sub_child in child:
                if issubclass(type(sub_child), javalang.parser.tree.Node):
                    children.append(__parse(sub_child, cdg))
    content_type = __parse_content_type(ast)
    line_range = __parse_line_range(ast, children)
    content = CDGContent(
        str(ast.__class__),
        content_type,
        line_range,
        name=str(getattr(ast, 'name', None)))
    cdg.add_node(content)
    for child in children:
        cdg.add_edge(content, child)
    if content_type == CDG_CONTENT_TYPE_FUNCTION:
        cdg.add_entry_point(content)
    return content


def __parse_content_type(ast: javalang.parser.tree.Node) -> str:
    return content_type_map.get(type(ast), CDG_CONTENT_TYPE_OBJECT)


def __parse_line_range(ast: javalang.parser.tree.Node, children: List[CDGContent]) -> Tuple[int, int]:
    return (
        (children[0].line_range[0] if children else -1) if ast.position is None else ast.position[0],
        children[-1].line_range[1] if children else (-1 if ast.position is None else ast.position[0]))

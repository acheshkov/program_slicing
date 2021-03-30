__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/29'

import javalang
from typing import List
from program_slicing.parse.node import \
    Node, \
    NODE_TYPE_FUNCTION, \
    NODE_TYPE_VARIABLE, \
    NODE_TYPE_ASSIGNMENT, \
    NODE_TYPE_CALL, \
    NODE_TYPE_STATEMENTS, \
    NODE_TYPE_BRANCH, \
    NODE_TYPE_LOOP, \
    NODE_TYPE_BREAK, \
    NODE_TYPE_GOTO, \
    NODE_TYPE_OBJECT, \
    NODE_TYPE_EXIT
from program_slicing.parse.block import Block
from program_slicing.parse.cg import ControlGraph


node_type_map = {
    javalang.parser.tree.VariableDeclaration:
        NODE_TYPE_VARIABLE,
    javalang.parser.tree.LocalVariableDeclaration:
        NODE_TYPE_VARIABLE,
    javalang.parser.tree.MethodDeclaration:
        NODE_TYPE_FUNCTION,
    javalang.parser.tree.IfStatement:
        NODE_TYPE_BRANCH,
    javalang.parser.tree.TryStatement:
        NODE_TYPE_BRANCH,
    javalang.parser.tree.WhileStatement:
        NODE_TYPE_LOOP,
    javalang.parser.tree.ForStatement:
        NODE_TYPE_LOOP,
    javalang.parser.tree.Assignment:
        NODE_TYPE_ASSIGNMENT,
    javalang.parser.tree.MethodInvocation:
        NODE_TYPE_CALL,
    javalang.parser.tree.BlockStatement:
        NODE_TYPE_STATEMENTS,
    javalang.parser.tree.ContinueStatement:
        NODE_TYPE_GOTO,
    javalang.parser.tree.BreakStatement:
        NODE_TYPE_BREAK,
    javalang.parser.tree.ReturnStatement:
        NODE_TYPE_EXIT
}


def parse(source_code: str) -> ControlGraph:
    """
    Parse the source code string into a Control Graph that contains Control Dependence and Control Flow.
    :param source_code: the string that should to be parsed
    :return: Control Graph
    """
    ast = javalang.parse.parse(source_code)
    result = ControlGraph()
    result.root = __parse(ast, result)
    return result


def __parse(ast: javalang.parser.tree.Node, cg: ControlGraph) -> Node:
    """
    Parse the javalang ast into a Node that contains Control Dependence
    and write Control Flow into the given Control Graph.
    :param ast: javalang node
    :param cg: Control Graph that will contain Control Flow
    :return: parsed Node
    """
    children = []
    for child in ast.children:
        if issubclass(type(child), javalang.parser.tree.Node):
            children.append(__parse(child, cg))
        elif type(child) is list or type(child) is set:
            for sub_child in child:
                if issubclass(type(sub_child), javalang.parser.tree.Node):
                    children.append(__parse(sub_child, cg))

    node_type = __parse_node_type(ast)
    if node_type == NODE_TYPE_BRANCH:
        __parse_block_branch(children, cg)
    elif node_type == NODE_TYPE_LOOP:
        __parse_block_loop(children, cg)
    elif children:
        __parse_block_other(children, cg)
    ids = (
        (children[0].ids[0] if children else -1) if ast.position is None else ast.position[0],
        children[-1].ids[1] if children else (-1 if ast.position is None else ast.position[0]))
    return Node(
        str(ast.__class__),
        node_type,
        ids,
        children=children)


def __parse_node_type(ast: javalang.parser.tree.Node) -> str:
    return node_type_map.get(type(ast), NODE_TYPE_OBJECT)


def __parse_block_branch(children: List[Node], cg: ControlGraph):
    condition_block = Block(
        nodes=[children[0]])
    cg.block[children[0]] = condition_block
    cg.block[children[-1]] = Block(
        nodes=[children[-1]],
        parents={condition_block})
    if len(children) == 3:
        cg.block[children[-2]] = Block(
            nodes=[children[-2]],
            parents={condition_block})


def __parse_block_loop(children: List[Node], cg: ControlGraph):
    condition_block = Block(
        nodes=[children[0]])
    cg.block[children[0]] = condition_block
    cg.block[children[-1]] = Block(
        nodes=[children[-1]],
        parents={condition_block},
        children={condition_block})


def __parse_block_other(children: List[Node], cg: ControlGraph):
    current_block = Block()
    for child in children:
        current_block.append(child)
        cg.block[child] = current_block
        if child.node_type == NODE_TYPE_BRANCH:
            current_block.add_child(cg.block.get(child.children[0], None))
            current_block = Block(
                parents={
                    cg.block[branch_child] for branch_child in child.children[-2:] if branch_child in cg.block})
        elif child.node_type == NODE_TYPE_LOOP:
            current_block.add_child(cg.block.get(child.children[0], None))
            current_block = Block(
                parents={cg.block[child.children[0]]} if child.children[0] in cg.block else {})
        elif child.children:
            current_block.add_child(cg.block.get(child.children[0], None))
            current_block = Block(
                parents={cg.block[child.children[-1]]} if child.children[0] in cg.block else {})

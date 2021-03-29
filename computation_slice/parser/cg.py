__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/23'

import javalang
from typing import Dict, Set
from computation_slice.parser.node import \
    Node, \
    NODE_TYPE_FUNCTION, \
    NODE_TYPE_VARIABLE, \
    NODE_TYPE_ASSIGNMENT, \
    NODE_TYPE_CALL, \
    NODE_TYPE_STATEMENTS, \
    NODE_TYPE_BRANCH, \
    NODE_TYPE_LOOP, \
    NODE_TYPE_CONTINUE, \
    NODE_TYPE_BREAK, \
    NODE_TYPE_GOTO, \
    NODE_TYPE_OBJECT, \
    NODE_TYPE_EXIT
from computation_slice.parser.block import Block


class ControlGraph:
    def __init__(self):
        self.root: Node = None
        self.block: Dict[Node: Block] = {}
        self.dom: Dict[Block: Set[Block]] = {}
        self.reach: Dict[Block: Set[Block]] = {}

    def get_dom(self, block: Block) -> Set[Block]:
        if block in self.dom:
            return self.dom[block]
        dom = set()
        # TODO: There should to be implemented fulfill of the dom
        self.dom[block] = dom
        return dom

    def get_reach(self, block: Block) -> Set[Block]:
        if block in self.reach:
            return self.reach[block]
        reach = set()
        # TODO: There should to be implemented fulfill of the reach
        self.reach[block] = reach
        return reach


def parse_java(source_code: str) -> ControlGraph:
    """
    Parse the source code string into a Control Graph that contains Control Dependence and Control Flow.
    :param source_code: the string that should to be parsed
    :return: Control Graph
    """
    ast = javalang.parse.parse(source_code)
    result = ControlGraph()
    result.root = __parse_java(ast, result)
    return result


def __parse_java(ast: javalang.parser.tree.Node, cg: ControlGraph) -> Node:
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
            children.append(__parse_java(child, cg))
        elif type(child) is list or type(child) is set:
            for sub_child in child:
                if issubclass(type(sub_child), javalang.parser.tree.Node):
                    children.append(__parse_java(sub_child, cg))

    node_type = __parse_java_node_type(ast)
    if node_type == NODE_TYPE_BRANCH:
        condition_block = Block(
            nodes=[children[0]])
        cg.block[children[0]] = condition_block
        cg.block[children[-1]] = Block(
            nodes=[children[-1]],
            parents={condition_block})
        if len(children) == 2:
            cg.block[children[-2]] = Block(
                nodes=[children[-2]],
                parents={condition_block})
    elif node_type == NODE_TYPE_LOOP:
        condition_block = Block(
            nodes=[children[0]])
        cg.block[children[0]] = condition_block
        cg.block[children[-1]] = Block(
            nodes=[children[-1]],
            parents={condition_block},
            children={condition_block})
    elif children:
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
    ids = (
        (children[0].ids[0] if children else -1) if ast.position is None else ast.position[0],
        children[-1].ids[1] if children else (-1 if ast.position is None else ast.position[0]))
    return Node(
        str(ast.__class__),
        node_type,
        ids,
        children=children)


def __parse_java_node_type(ast: javalang.parser.tree.Node) -> str:
    if \
            type(ast) is javalang.parser.tree.VariableDeclaration:
        return NODE_TYPE_VARIABLE
    if \
            type(ast) is javalang.parser.tree.MethodDeclaration:
        return NODE_TYPE_FUNCTION
    elif \
            type(ast) is javalang.parser.tree.IfStatement or \
            type(ast) is javalang.parser.tree.TryStatement:
        return NODE_TYPE_BRANCH
    elif \
            type(ast) is javalang.parser.tree.WhileStatement or \
            type(ast) is javalang.parser.tree.ForStatement:
        return NODE_TYPE_LOOP
    else:
        return NODE_TYPE_OBJECT

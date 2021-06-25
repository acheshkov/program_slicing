__licence__ = 'MIT'
__author__ = 'lyriccoder'
__credits__ = ['lyriccoder, kuyaki']
__maintainer__ = 'lyriccoder'
__date__ = '2021/05/20'

import itertools
from itertools import combinations_with_replacement
from typing import Tuple, Iterator, List, Dict, Optional, Any

import tree_sitter
from tree_sitter import Node

from program_slicing.graph.parse import tree_sitter_ast
from program_slicing.graph.parse import tree_sitter_parsers
from program_slicing.graph.point import Point


def get_block_slices(source_code: str, lang: str) -> \
        List[Tuple[
            Point,
            Point
        ]]:
    """
    Return opportunities list.
    :param source_code: source code that should be decomposed.
    :param lang: string with the source code format described as a file ext (like '.java' or '.xml').
    :return: list of tuples where first item is start point, last item is end point.
    """
    # filter_wrong_statements(source_code, lang)
    statements_by_block_id: Dict[int, List[tree_sitter.Node]] = __determine_unique_blocks(source_code, lang)
    if not statements_by_block_id:
        return []
    statements_combinations_by_block_id = __generate_all_possible_opportunities(statements_by_block_id)
    ranges = __count_block_bounds(statements_combinations_by_block_id)
    # we subtract  since we added class and method to the block of the passed code
    return sorted(list(itertools.chain(*ranges)), key=lambda x: (x[0][0], x[1][0]))


def __determine_unique_blocks(source_code: str, lang: str) -> Dict[int, List[tree_sitter.Node]]:
    """
    Gets unique blocks.
    :param source_code: source code that should be analyzed.
    :param lang: string with the source code format described as a file ext (like '.java' or '.xml').
    :return: dict with unique key, where value is block.
    """
    counter = 0
    statements_by_block_id: Dict[int, List[tree_sitter.Node]] = {}
    ast = tree_sitter_ast(source_code, lang).root_node
    source_code_bytes = bytes(source_code, "utf-8")
    block_nodes_and_levels = (
        (block_node, level)
        for block_node, level in __get_block_nodes_per_level(ast)
        if not __ast_contains_outer_goto(source_code_bytes, block_node)
    )
    for block_node, level in block_nodes_and_levels:
        named_node = block_node.children[0]
        named_node = named_node if named_node.is_named else named_node.next_named_sibling
        statements_by_block_id[counter] = []
        while named_node:
            statements_by_block_id[counter].append(named_node)
            named_node = named_node.next_named_sibling
        if statements_by_block_id[counter]:
            counter += 1
    return statements_by_block_id


def __traverse_ast(root: tree_sitter.Node, level=0) -> Iterator[Tuple[tree_sitter.Node, int]]:
    """
    Traverse ast.
    :param root: node to start traversing.
    :param level: start level.
    :return: child with level.
    """
    for child in root.children:
        for ast_and_level in __traverse_ast(child, level + 1):
            yield ast_and_level
    yield root, level


def __get_block_nodes_per_level(root: tree_sitter.Node) -> Iterator[Tuple[tree_sitter.Node, int]]:
    """
    Returns block with level number in ast tree.
    :param root: node to start finding.
    :return: found node with level.
    """
    for ast, level in __traverse_ast(root):
        # get blocks for cycles, etc.
        body_node = ast.child_by_field_name("body")
        # get blocks for if statement
        consequence_node = ast.child_by_field_name("consequence")
        # get blocks for else statement
        alternative_node = ast.child_by_field_name("alternative")
        if body_node is not None:
            yield body_node, level
        elif consequence_node is not None:
            yield consequence_node, level
            if alternative_node is not None:
                yield alternative_node, level
        elif ast.type == "finally_clause":
            if len(ast.children) > 1:
                yield ast.children[1], level
        elif ast.type == "program":
            if {
                "class_declaration",
                "enum_declaration",
                "interface_declaration",
            }.intersection({node.type for node in ast.children}):
                continue
            yield ast, level


def __ast_contains_outer_goto(source_code_bytes: bytes, ast: Node, hooks: Dict[str, int] = None) -> bool:
    if hooks is None:
        hooks = {}
    ast_name = tree_sitter_parsers.node_name(source_code_bytes, ast)
    ast_name = 0 if ast_name is None else ast_name
    ast_is_goto = \
        ast.type == "break_statement" or \
        ast.type == "continue_statement"
    ast_is_hook = \
        ast.type == "labeled_statement" or \
        ast.type == "for_statement" or \
        ast.type == "enhanced_for_statement" or \
        ast.type == "while_statement"
    if ast_is_goto:
        if ast_name not in hooks:
            return True
    elif ast_is_hook:
        val = hooks.get(ast_name, 0)
        hooks[ast_name] = val + 1
    if ast.children:
        for child in ast.children:
            if __ast_contains_outer_goto(source_code_bytes, child, hooks):
                return True
    if ast_is_hook:
        val = hooks.get(ast_name, None)
        if val <= 1:
            del hooks[ast_name]
        else:
            hooks[ast_name] = val - 1
    return False


def __generate_all_possible_opportunities(
        statements_by_block_id: Dict[int, List[tree_sitter.Node]]) -> Dict[int, List[List[Node]]]:
    """
    Get all possible combinations of blocks.
    :param statements_by_block_id: dict with unique blocks.
    :return: dict with combinations of statements for block.
    """
    statements_combinations_by_block_id = {}
    for block_id, statements in statements_by_block_id.items():
        id_combinations = [c for c in combinations_with_replacement([idx for idx in range(len(statements))], 2)]
        statements_combinations = [statements[ids[0]: ids[1] + 1] for ids in id_combinations]
        statements_combinations_by_block_id[block_id] = statements_combinations
    return statements_combinations_by_block_id


def __count_block_bounds(statements_combinations_by_block_id) -> List[List[Tuple[Optional[Any], Optional[Any]]]]:
    """
    Count min and max lines for blocks.
    :param statements_combinations_by_block_id: dict with unique blocks.
    Key is unique int, value is list of ranges.
    :return: List of line ranges.
    """
    ranges_by_block_id = {}
    for block_id, statements_combinations in statements_combinations_by_block_id.items():
        ranges = []
        for statements_combination in statements_combinations:
            start_point = None
            end_point = None
            for statement in statements_combination:
                if start_point is None or statement.start_point < start_point:
                    start_point = statement.start_point
                if end_point is None or statement.end_point > end_point:
                    end_point = statement.end_point
            ranges.append((start_point, end_point))
        ranges_by_block_id[block_id] = ranges

    return [list(x) for x in ranges_by_block_id.values()]

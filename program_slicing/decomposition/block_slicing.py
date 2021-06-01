import itertools
from itertools import combinations_with_replacement
from typing import Tuple, Iterator, List, Dict, Optional, Any

import tree_sitter
from tree_sitter import Node

from program_slicing.graph.parse import cdg_java
from program_slicing.graph.parse import tree_sitter_parsers
from program_slicing.graph.statement import StatementLineNumber, StatementColumnNumber

parse_node_name = cdg_java.__parse_statement_name


def traverse_ast(root: tree_sitter.Node, level=0) -> Iterator[Tuple[tree_sitter.Node, int]]:
    """
    Traverse ast

    :param root: node to start traversing
    :param level: start level
    :return: child with level
    """
    for child in root.children:
        for ast_and_level in traverse_ast(child, level + 1):
            yield ast_and_level
    yield root, level


def get_block_nodes_per_level(root: tree_sitter.Node) -> Iterator[Tuple[tree_sitter.Node, int]]:
    """
    Returns block with level number in ast tree

    :param root: node to start finding
    :return: found node with level
    """
    for ast, level in traverse_ast(root):
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
        elif alternative_node is not None:
            yield alternative_node, level
        elif ast.type == "finally_clause":
            if len(ast.children) > 1:
                yield ast.children[1], level


def get_opportunities_list(source_code: str) -> List[Tuple[StatementLineNumber, StatementColumnNumber]]:
    """
    Return opportunities list.

    :param source_code: java code
    :return: list of tuples where first item is start point, last item is end ponit
    """
    statements_by_block_id: Dict[int, List[tree_sitter.Node]] = determine_unique_blocks(source_code)
    if not statements_by_block_id:
        return []
    statements_combinations_by_block_id = generate_all_possible_opportunities(statements_by_block_id)
    ranges = count_block_bounds(statements_combinations_by_block_id)
    # we subtract  since we added class and method to the block of the passed code
    return sorted(list(itertools.chain(*ranges)), key=lambda x: (x[0][0], x[1][0]))


def count_block_bounds(statements_combinations_by_block_id) \
        -> List[List[Tuple[Optional[Any], Optional[Any]]]]:
    """
    Count min and max lines for blocks

    :param statements_combinations_by_block_id: dict with unique blocks.
    Key is unique int, value is list of ranges
    :return: List of line ranges
    """
    ranges_by_block_id = {}
    for block_id, statements_combinations in statements_combinations_by_block_id.items():
        ranges = []
        for statements_combination in statements_combinations:
            start_point = None
            end_point = None
            for statement in statements_combination:
                if start_point is None or statement.start_point[0] < start_point[0] or (
                        statement.start_point[0] == start_point[0] and statement.start_point[1] < start_point[1]):
                    start_point = statement.start_point
                if end_point is None or statement.end_point[0] > end_point[0] or (
                        statement.end_point[0] == end_point[0] and statement.end_point[1] > end_point[1]):
                    end_point = statement.end_point
            ranges.append((start_point, end_point))
        ranges_by_block_id[block_id] = ranges

    return [list(x) for x in ranges_by_block_id.values()]


def generate_all_possible_opportunities(statements_by_block_id: Dict[int, List[tree_sitter.Node]]) \
        -> Dict[int, List[List[Node]]]:
    """
    Get all possible combinations of blocks

    :param statements_by_block_id: dict with unique blocks
    :return: dict with combinations of statements for block
    """
    statements_combinations_by_block_id = {}
    for block_id, statements in statements_by_block_id.items():
        id_combinations = [c for c in combinations_with_replacement([idx for idx in range(len(statements))], 2)]
        statements_combinations = [statements[ids[0]: ids[1] + 1] for ids in id_combinations]
        statements_combinations_by_block_id[block_id] = statements_combinations
    return statements_combinations_by_block_id


def find_first_function(source_code_bytes: bytes, root: tree_sitter.Node, name: str) \
        -> Optional[tree_sitter.Node]:
    """
    Find first matched function by name

    :param source_code_bytes: java code
    :param root: root Node to start search
    :param name: function name
    :return: Node with function or None if it is not found
    """
    for ast, level in traverse_ast(root):
        if ast.type == "method_declaration":
            found_name = parse_node_name(source_code_bytes, ast.child_by_field_name("name"))
            if name == found_name:
                return ast
    return None


def determine_unique_blocks(source_code: str) -> Dict[int, List[tree_sitter.Node]]:
    """
    Gets unique blocks
    :param source_code: java code
    :return: dict with unique key, where value is block
    """

    counter = 0
    statements_by_block_id: Dict[int, List[tree_sitter.Node]] = {}
    surrounded_code = surround_with_class_and_method(source_code)
    source_code_bytes = bytes(surrounded_code, "utf8")
    ast = tree_sitter_parsers.java().parse(source_code_bytes).root_node

    function = find_first_function(source_code_bytes, ast, 'function')
    for block_node, level in get_block_nodes_per_level(function):
        named_node = block_node.children[0]
        named_node = named_node if named_node.is_named else named_node.next_named_sibling
        statements_by_block_id[counter] = []
        while named_node:
            statements_by_block_id[counter].append(named_node)
            named_node = named_node.next_named_sibling
        if statements_by_block_id[counter]:
            counter += 1
    return statements_by_block_id


def surround_with_class_and_method(code: str) -> str:
    """
    Surrounds block of code with function and class.

    :param code: Java code
    :return java code
    """
    return f'class Foo {{ public void function() {{{code}}} }}'

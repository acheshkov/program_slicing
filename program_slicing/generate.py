from itertools import combinations_with_replacement
from typing import Tuple, Iterator, List, Dict

import tree_sitter

from program_slicing.graph.parse import cdg_java
from program_slicing.graph.parse import tree_sitter_parsers

parse_node_name = cdg_java.__parse_statement_name


def traverse_ast(root: tree_sitter.Node, level=0) -> Iterator[Tuple[tree_sitter.Node, int]]:
    for child in root.children:
        for ast_and_level in traverse_ast(child, level + 1):
            yield ast_and_level
    yield root, level


def get_function_nodes(root: tree_sitter.Node) -> Iterator[tree_sitter.Node]:
    for ast, level in traverse_ast(root):
        if ast.type == "method_declaration" or ast.type == "constructor_declaration":
            yield ast


def get_block_nodes(root: tree_sitter.Node) -> Iterator[Tuple[tree_sitter.Node, int]]:
    for ast, level in traverse_ast(root):
        body_node = ast.child_by_field_name("body")
        consequence_node = ast.child_by_field_name("consequence")
        alternative_node = ast.child_by_field_name("alternative")
        if body_node is not None:
            yield body_node, level
        elif consequence_node is not None:
            yield consequence_node, level
        elif alternative_node is not None:
            yield alternative_node, level


def generate_possible_opportunities(filename: str, function_name: str, start_line: int):
    with open(filename) as f:
        source_code = f.read()

    statements_by_block_id = generate_all_possible_blocks(function_name, source_code, start_line)

    statements_combinations_by_block_id = {}
    for block_id, statements in statements_by_block_id.items():
        id_combinations = [c for c in combinations_with_replacement([idx for idx in range(len(statements))], 2)]
        statements_combinations = [statements[ids[0]: ids[1] + 1] for ids in id_combinations]
        statements_combinations_by_block_id[block_id] = statements_combinations

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

    print(ranges_by_block_id)


def generate_all_possible_blocks(function_name: str, source_code: str, start_line: int):
    counter = 0
    statements_by_block_id: Dict[int, List[tree_sitter.Node]] = {}
    source_code_bytes = bytes(source_code, "utf8")
    ast = tree_sitter_parsers.java().parse(source_code_bytes).root_node
    for function_node in get_function_nodes(ast):
        node_name = parse_node_name(source_code_bytes, function_node.child_by_field_name("name"))
        if node_name == function_name and function_node.start_point[0] == start_line:
            for block_node, level in get_block_nodes(function_node):
                named_node = block_node.children[0]
                named_node = named_node if named_node.is_named else named_node.next_named_sibling
                statements_by_block_id[counter] = []
                while named_node is not None:
                    statements_by_block_id[counter].append(named_node)
                    named_node = named_node.next_named_sibling
                if statements_by_block_id[counter]:
                    counter += 1
    return statements_by_block_id


if __name__ == '__main__':
    generate_possible_opportunities(
        r'Logo.java',
        'all',
        13)

__licence__ = 'MIT'
__author__ = 'lyriccoder'
__credits__ = ['lyriccoder, kuyaki']
__maintainer__ = 'lyriccoder'
__date__ = '2021/05/20'

import itertools
import operator
from collections import defaultdict
from functools import reduce
from itertools import combinations_with_replacement
from typing import Tuple, Iterator, List, Dict, Optional, Any

import tree_sitter
from tree_sitter import Node

from program_slicing.graph.ddg import DataDependenceGraph
from program_slicing.graph.manager import ProgramGraphsManager
from program_slicing.graph.parse import tree_sitter_ast
from program_slicing.graph.parse import tree_sitter_parsers
from program_slicing.graph.parse.tree_sitter_parsers import node_name
from program_slicing.graph.point import Point
from program_slicing.graph.statement import Statement


def filter_blocks_by_range(x, y, min_range: int, max_range: int):
    diff = x - y
    if (diff > min_range) and (diff < max_range):
        return False
    else:
        return True


def find_real_block(block, block_lines_ranges):
    cur_block_start_line, cur_block_end_line = block
    results_with_diff = {}
    for block_id, lines in block_lines_ranges.items():
        start_point = lines[0]
        end_point = lines[1]
        if (cur_block_start_line[0] >= start_point) and (cur_block_end_line[0] <= end_point):
            results_with_diff[block_id] = (start_point, end_point)

    # return the closest block
    blocks_with_diff = {}
    for block_id, block_lines in results_with_diff.items():
        potential_block_start_line, potential_block_end_line = block_lines
        total_diff = (cur_block_start_line[0] - potential_block_start_line) \
                     + (cur_block_end_line[0] - potential_block_end_line)
        blocks_with_diff[block_id] = total_diff

    return sorted(blocks_with_diff.items(), key=lambda x: x[1], reverse=True)[0][0]


def get_privitive_types(var_affected, all_statements):
    prohibited_types = {
        'Character', 'Byte', 'Short', 'Integer', 'Long',
        'Float', 'Double', 'Boolean',
        'character', 'byte', 'short', 'int', 'long',
        'float', 'double', 'boolean', 'String'
    }
    filtered_vars_list = []
    for var_stat in var_affected:
        statements_by_line = all_statements.get(var_stat.start_point.line_number)
        type = [x for x in statements_by_line if x.ast_node_type in ['type_identifier', 'integral_type']][0]
        if type.name in prohibited_types:
            filtered_vars_list.append(var_stat)
    return filtered_vars_list


def get_block_slices(source_code: str, lang: str, min_range=5, max_percentage=0.8) -> \
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
    all_lines = source_code.split('\n')
    statements_by_block_id, blocks_by_level = __determine_unique_blocks(source_code, lang)
    if not statements_by_block_id:
        return []

    block_indexes_by_range, blocks_by_min_line = get_block_tables(statements_by_block_id)
    statements_combinations_by_block_id = __generate_all_possible_opportunities(statements_by_block_id)
    block_ranges = __count_combinations_blocks_bounds(statements_combinations_by_block_id)

    # we subtract since we added class and method to the cur_block of the passed code
    reduced_blocks = clean_blocks(block_ranges, all_lines, min_range, max_percentage)

    filtered_blocks_list = set()

    manager_by_source = ProgramGraphsManager(source_code, lang)
    ddg = manager_by_source.get_data_dependence_graph()
    declarations, all_statements = get_statements_dict(ddg)

    for cur_block in reduced_blocks:
        block_start_line = cur_block[0][0]
        block_end_line = cur_block[1][0]
        cur_block_range = range(block_start_line, block_end_line + 1)
        lines_for_cur_block = set(cur_block_range)
        expanded_block_id = find_real_block(cur_block, block_indexes_by_range)
        # extend opportunity to cur_block
        real_min_line, real_max_line = block_indexes_by_range[expanded_block_id]
        rest_lines = set(range(block_start_line, real_max_line + 1)).difference(lines_for_cur_block)
        if not rest_lines:
            filtered_blocks_list.add(cur_block)
            continue

        var_declarations_in_cur_block = [
            declarations.get(line) for line in lines_for_cur_block if
            declarations.get(line)]
        if var_declarations_in_cur_block:
            var_declarations_in_cur_block = reduce(
                operator.concat, var_declarations_in_cur_block)
        else:
            filtered_blocks_list.add(cur_block)
            continue

        if do_filter_block_by_variable_usage(
                all_statements,
                ddg,
                rest_lines,
                var_declarations_in_cur_block):
            filtered_blocks_list.add(cur_block)

    return sorted(filtered_blocks_list, key=lambda x: (x[0][0], x[1][0]))


def do_filter_block_by_variable_usage(
        all_statements,
        ddg,
        rest_lines,
        var_declarations_in_cur_block):
    """
    Return True if we need to filter this block.

    :param all_statements: dict with key as line number and values as list of Statements
    :param ddg: Graph
    :param rest_lines: Lines after current block in the same scope
    :param var_declarations_in_cur_block: Dict with variables in the current block
    :return: True if we need to filter that block
    """
    var_affected = []
    for var_statement in var_declarations_in_cur_block:
        lines_which_var_used = get_lines_where_var_was_used(ddg, var_statement)
        if lines_which_var_used:
            lines_which_var_used = set(reduce(
                operator.concat, lines_which_var_used))
        else:
            continue
        found_lines = lines_which_var_used.intersection(rest_lines)
        if found_lines:
            var_affected.append(var_statement)
    primitive_var_affected = get_privitive_types(var_affected, all_statements)
    if len(primitive_var_affected) < 2:
        return True

    return False


def clean_blocks(block_ranges, all_lines, min_range_to_filter, max_percentage_to_filter):
    """
    Clean unnecessary blocks since we surround code with method and class.

    :param block_ranges:
    :param min_range_to_filter: minimum number of lines of EMOs which are allowed
    :param max_percentage_to_filter: max percentage EMO in comparison to all length of snippet which is allowed
    :return: allowed EMOs
    """
    blocks_list = set(itertools.chain(*block_ranges))
    reduced_blocks = filter(lambda x: x[1][0] - x[0][0] > min_range_to_filter, blocks_list)
    reduced_blocks = filter(lambda x: (x[1][0] - x[0][0]) / len(all_lines) <= max_percentage_to_filter, reduced_blocks)
    return reduced_blocks


def get_block_tables(statements_by_block_id):
    block_lines_ranges = {}
    block_min_line = {}
    for block_index, y in statements_by_block_id.items():
        lines = []
        for j in y:
            lines.extend(list(range(j.start_point[0], j.end_point[0] + 1)))

        lines = set(lines)
        block_lines_ranges[block_index] = (min(lines), max(lines))
        block_min_line[min(lines)] = block_index
    return block_lines_ranges, block_min_line


def get_all_affected_statements(ddg, statement, results):
    for successor in ddg.successors(statement):
        if successor in results:
            continue
        results.add(successor)
        get_all_affected_statements(ddg, successor, results)


def get_lines_where_var_was_used(ddg, var_statement):
    results = set()
    get_all_affected_statements(ddg, var_statement, results)
    lines_which_var_used = [
        list(range(x.start_point.line_number, x.end_point.line_number + 1))
        for x in results]
    return lines_which_var_used


def get_statements_dict(ddg):
    """
    Get all variables declarations and its names which can be obtained by line number.
    Get table of all statements which can be obtained by line number
    :param ddg:
    :return:
    """
    var_decl = defaultdict(list)
    all_stats = defaultdict(list)
    for stat in ddg:
        if stat.ast_node_type == 'variable_declarator':
            var_decl[stat.start_point.line_number].append(stat)
        all_stats[stat.start_point.line_number].append(stat)
    return var_decl, all_stats


def __determine_unique_blocks(source_code: str, lang: str) \
        -> Tuple[Dict[int, List[tree_sitter.Node]], Dict[int, int]]:
    """
    Gets unique blocks.
    :param source_code: source code that should be analyzed.
    :param lang: string with the source code format described as a file ext (like '.java' or '.xml').
    :return: dict with unique key, where value is block.
    """
    counter = 0
    statements_by_block_id: Dict[int, List[tree_sitter.Node]] = {}
    blocks_by_level = defaultdict(list)
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
            blocks_by_level[level].append(named_node)
            statements_by_block_id[counter].append(named_node)
            named_node = named_node.next_named_sibling
        if statements_by_block_id[counter]:
            counter += 1
    return statements_by_block_id, blocks_by_level


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


def __count_combinations_blocks_bounds(statements_combinations_by_block_id) -> List[
    List[Tuple[Optional[Any], Optional[Any]]]]:
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

__licence__ = 'MIT'
__author__ = 'lyriccoder'
__credits__ = ['lyriccoder, kuyaki']
__maintainer__ = 'lyriccoder'
__date__ = '2021/05/20'

import itertools
import operator
from collections import defaultdict, OrderedDict
from functools import reduce
from itertools import combinations_with_replacement
from typing import Tuple, Iterator, List, Dict, Optional, Any

import tree_sitter
from tree_sitter import Node

from program_slicing.graph.ddg import DataDependenceGraph
from program_slicing.graph.manager import ProgramGraphsManager
from program_slicing.graph.parse import tree_sitter_ast, data_dependence_graph, LANG_JAVA
from program_slicing.graph.parse import tree_sitter_parsers
from program_slicing.graph.parse.tree_sitter_parsers import node_name
from program_slicing.graph.statement import StatementLineNumber, StatementColumnNumber


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
        if (start_point >= cur_block_start_line[0]) and (cur_block_end_line[0] <= end_point):
            results_with_diff[block_id] = (start_point, end_point)

    # return the closest block
    blocks_with_diff = {}
    for block_id, block_lines in results_with_diff.items():
        potential_block_start_line, potential_block_end_line = block_lines
        total_diff = (cur_block_start_line[0] - potential_block_start_line) \
                     + (cur_block_end_line[0] - potential_block_end_line)
        blocks_with_diff[block_id] = total_diff

    return sorted(blocks_with_diff.items(), key=lambda x: x[1], reverse=True)[0][0]


# def remove_useless_var_decl(var_decl, all_statements, cur_block_range, cfg):
#     cur_var_decl = [var_decl.get(line) for line in cur_block_range if var_decl.get(line)]
#     cycles_and_try_resources = []
#     for bb in cfg:
#         for stat in bb.get_statements():
#             if stat.ast_node_type in ['for_statement', '']:
#                 cycles_and_try_resources.append(stat)
#
#     needed_var_decl = []
#     for var_statement in cur_var_decl:
#         for node in cycles_and_try_resources:
#             if not cfg.has_successor(node, var_statement):
#                 needed_var_decl.append(var_statement)




    # for start_point, var_name in var_decl.items():
    #     elems = v[start_point]
    #     found_var_decl_in_cfg = [x for x in elems if x.ast_node_type == 'variable_declarator' and name == ''][0]
    #     print(found_var_decl_in_cfg)



def get_block_slices(source_code: str, lang: str, min_range=5, max_percentage=0.8) -> \
        List[Tuple[
            Tuple[StatementLineNumber, StatementColumnNumber],
            Tuple[StatementLineNumber, StatementColumnNumber]
        ]]:
    """
    Return opportunities list.
    :param source_code: source code that should be decomposed.
    :param lang: string with the source code format described as a file ext (like '.java' or '.xml').
    :return: list of tuples where first item is start point, last item is end point.
    """
    # filter_wrong_statements(source_code, lang)
    all_lines = source_code.split('\n')
    source_code_bytes = bytes(source_code, "utf-8")
    statements_by_block_id, blocks_by_level = __determine_unique_blocks(source_code, lang)
    if not statements_by_block_id:
        return []

    block_lines_ranges = {}
    block_min_line = {}

    for block_index, y in statements_by_block_id.items():
        lines = []
        for j in y:
            lines.extend(list(range(j.start_point[0], j.end_point[0] + 1)))

        lines = set(lines)
        block_lines_ranges[block_index] = (min(lines), max(lines))
        block_min_line[min(lines)] = block_index

    # sorted_block_ranges = OrderedDict(sorted(block_lines_ranges.items(), key=lambda x: x[1][0]))
    # tree_blocks = {}
    # # add the first block
    # min_line, max_line = sorted_block_ranges[0]
    # tree_blocks[0].append({'min_line': min_line, 'max_line': max_line, 'prev': None})
    # for cur_index, lines_range in sorted_block_ranges.items():
    #     if cur_index == 0:
    #         continue
    #     prev_lines = block_lines_ranges.get(cur_index - 1)
    #     min_line, max_line = lines_range
    #
    #     for block_idx, inner_blocks in tree_blocks.items():
    #         # if we found
    #         if (inner_blocks['min_line'] > min_line) and (inner_blocks['max_line'] <= max_line):
    #
    #         inner_blocks.add({'min_line': min_line, 'max_line': max_line, 'prev': block_idx - 1})


    statements_combinations_by_block_id = __generate_all_possible_opportunities(statements_by_block_id)
    ranges = __count_block_bounds(statements_combinations_by_block_id)

    # we subtract since we added class and method to the block of the passed code
    blocks_list = set(itertools.chain(*ranges))
    reduced_blocks = filter(lambda x: x[1][0] - x[0][0] > min_range, blocks_list)
    reduced_blocks = filter(lambda x: len(all_lines) / (x[1][0] - x[0][0]) > max_percentage, reduced_blocks)

    filtered_blocks_list = set()
    # var_decl = defaultdict(set)

    manager_by_source = ProgramGraphsManager(source_code, lang)
    cfg = manager_by_source.get_control_flow_graph()

    lines_affected_by = defaultdict(set)

    var_decl, all_statements = get_statements_dict(cfg)
    # for s in ddg:
    #     if s.ast_node_type == 'variable_declarator':
    #         blocks = manager_by_source.get_basic_block(s)
    #         is_inside_for = blocks.get_statements()[-1].ast_class == 'for_statement'
    #         if not blocks and not is_inside_for:
    #             # vae not inside for

    # for x in s.affected_by:
    #
    #     lines_affected_by[s.start_point[0]].add(x)
    print(lines_affected_by)
    # prohibited_types = {
    #     'Character', 'Byte', 'Short', 'Integer', 'Long',
    #     'Float', 'Double', 'Boolean',
    #     'character', 'byte', 'short', 'integer', 'long',
    #     'float', 'double', 'boolean'
    # }

    # [x[0][0], x[1][0] for x in reduced_blocks if ]

    all_lines_with_var_decl = set(var_decl.keys())
    for block in reduced_blocks:
        print(block)
        block_start_line = block[0][0]
        block_end_line = block[1][0]
        cur_block_range = range(block_start_line, block_end_line + 1)
        lines_for_cur_block = set(cur_block_range)
        # remove_useless_var_decl(var_decl, all_statements, cur_block_range, cfg)
        # find real block, find rest of blocks find whether we use it


        lines_with_var_decl_for_cur_block = lines_for_cur_block.intersection(all_lines_with_var_decl)
        if len(lines_with_var_decl_for_cur_block) < 2:
            # more than 2 declarations, we can't return more than 2 objects in Java
            filtered_blocks_list.add(block)
        else:
            block_id = find_real_block(block, block_lines_ranges)
            # extend opportunity to block
            real_min_line, real_max_line = block_lines_ranges[block_id]
            rest_lines = set(range(block_start_line, real_max_line)).difference(lines_for_cur_block)
            # continue
            var_affected = []
            for bb in cfg:
                for s in bb.get_statements():
                    if (s.start_point[0] in rest_lines) and (s.end_point[0] in rest_lines):
                        var_affected.extend(s.affected_by)
            # remove variables declared in loops
            var_affected = set(var_affected)
            # check if the rest of statements affected by variables
            var_affected = var_affected.intersection(set().union(*var_decl.values()))
            if len(var_affected) < 2:
                filtered_blocks_list.add(block)

            # statements_for_cur_block = [j for j in ddg if
            #  (j.start_point[0] in lines_for_cur_block) and
            #  (j.end_point[0] in lines_for_cur_block)]

            # stats_depended = [[ddg.successors(x)] for x in statements_for_cur_block]
            # # TODO find all usage of easy types (int, short)
            # cur_start_line = 9999999999
            #
            # while cur_start_line > block_start_line:
            #     cur_start_line = block_start_line
            #
            # block_index = block_min_line.get(cur_start_line)
            # real_min_block_line, real_max_block_line = block_lines_ranges.get(block_index)
            # print('----------------------------------------')
            #
            # lines_for_curr_block = range(block_start_line, block_end_line + 1)
            # lines_with_var_decl_for_block = {x for x in var_decl if x in lines_for_curr_block}
            # lines_outside_block = set(range(real_min_block_line, real_max_block_line)).difference(lines_for_curr_block)
            # for line in lines_outside_block:
            #     vars_affected = lines_affected_by.get(line, [])
            #     proh_vars = [x for x in vars_affected
            #                  # if (x.type in prohibited_types)
            #                  if (x.name in lines_with_var_decl_for_block)]
            #     if len(proh_vars) < 2:
            #         # lines_where_var_declared = var_decl.get(proh_vars)
            #         # real_affected_lines = [x for x in line if line in lines_where_var_declared]
            #         # if len(real_affected_lines) < 2:
            #         filtered_blocks_list.add(block)
            #         # print(f'{all_lines[line]}')

    return sorted(filtered_blocks_list, key=lambda x: (x[0][0], x[1][0]))


def get_statements_dict(cfg):
    # root = tree_sitter_ast(source_code, lang).root_node
    # for ast, level in __traverse_ast(root):
    #     if ast.type == 'variable_declarator':
    #         if ast.parent.parent.type != 'for_statement':
    #             var_name = node_name(source_code_bytes, ast)
    #             var_decl[ast.start_point[0]].add(var_name)
    var_decl = {}
    all_stats = defaultdict(list)
    for bb in cfg:
        for stat in bb.get_statements():
            if stat.ast_node_type == 'variable_declarator':
                var_decl[stat.start_point[0]] = stat
            all_stats[stat.start_point[0]].append(stat)
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
                if start_point is None or statement.start_point[0] < start_point[0] or (
                        statement.start_point[0] == start_point[0] and statement.start_point[1] < start_point[1]):
                    start_point = statement.start_point
                if end_point is None or statement.end_point[0] > end_point[0] or (
                        statement.end_point[0] == end_point[0] and statement.end_point[1] > end_point[1]):
                    end_point = statement.end_point
            ranges.append((start_point, end_point))
        ranges_by_block_id[block_id] = ranges

    return [list(x) for x in ranges_by_block_id.values()]

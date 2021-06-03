import itertools
from collections import defaultdict, OrderedDict
from operator import itemgetter
from typing import List, Dict, Optional, Tuple

import tree_sitter
from tree_sitter import Node

from program_slicing.decomposition.slicing import get_complete_computation_slices
from program_slicing.graph.parse.parse import LANG_JAVA, tree_sitter_ast

from program_slicing.decomposition.block_slicing import get_block_slices, __get_block_nodes_per_level, __traverse_ast


def __determine_unique_blocks_with_level(source_code: str, lang: str):
    """
    Gets unique blocks.
    :param source_code: source code that should be analyzed.
    :param lang: string with the source code format described as a file ext (like '.java' or '.xml').
    :return: dict with unique key, where value is block.
    """
    counter = 0
    statements_by_block_id = {}
    ast = tree_sitter_ast(source_code, lang).root_node
    for block_node, level in __get_block_nodes_per_level(ast):
        named_node = block_node.children[0]
        named_node = named_node if named_node.is_named else named_node.next_named_sibling
        statements_by_block_id[counter] = []
        while named_node:
            statements_by_block_id[counter].append((named_node, level))
            named_node = named_node.next_named_sibling
        if statements_by_block_id[counter]:
            counter += 1
    return statements_by_block_id


def __count_block_bounds(statements_combinations_by_block_id):
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

    return ranges_by_block_id


class BlockNode(object):

    def __init__(self):
        self.__prev = Optional[BlockNode]
        self.__start = Optional[int]
        self.__end = Optional[int]
        self.__next = Optional[BlockNode]
        self.__node = Optional[Node]
        self.__level = Optional[int]

    @property
    def prev(self):
        return self.__prev

    @prev.setter
    def prev(self, prev):
        self.__prev = prev

    @property
    def next(self):
        return self.__next

    @next.setter
    def next(self, next):
        self.__next = next

    @property
    def start(self):
        return self.__start

    @start.setter
    def start(self, start):
        self.__start = start

    @property
    def end(self):
        return self.__end

    @end.setter
    def end(self, end):
        self.__end = end


def construct_block_nodes_as_tree(ranges_by_block_id):
    ranges_by_block_id_c = ranges_by_block_id.copy()
    while ranges_by_block_id_c:
        min_start_point, _ = min(ranges_by_block_id_c.items(), key=lambda x: (x[1][0], x[1][1]))


def create_tree():
    global nodeBlock
    sorted_ranges_by_block_id = sorted(ranges_by_block_id.items(), key=lambda x: (x[1][0], x[1][1]))
    nodeBlock = BlockNode()
    nodeBlock.prev = None
    nodeBlock.start = sorted_ranges_by_block_id[0][1][0]
    nodeBlock.end = sorted_ranges_by_block_id[0][1][1]
    for id, item in sorted_ranges_by_block_id[1:]:
        start, end, level = item
        if (start >= nodeBlock.start) and (end <= nodeBlock.end):
            newNodeBlock = BlockNode()
            newNodeBlock.start = start
            newNodeBlock.end = end
            nodeBlock.next = newNodeBlock
            newNodeBlock.prev = nodeBlock
            nodeBlock = newNodeBlock
        else:
            # prev = nodeBlock.prev
            nodeBlock = nodeBlock.prev
            while nodeBlock:
                if (start >= nodeBlock.start) and (end <= nodeBlock.end):
                    newNodeBlock = BlockNode()
                    newNodeBlock.start = start
                    newNodeBlock.end = end
                    next_copy = nodeBlock.next
                    nodeBlock.next = newNodeBlock
                    newNodeBlock.prev = nodeBlock
                    newNodeBlock.next = next_copy
                    nodeBlock = newNodeBlock
                    break
                else:
                    # prev = nodeBlock.prev
                    nodeBlock = nodeBlock.prev


def create_tree_by_level(dict_with_blocks):
    new_dict = defaultdict(list)
    for block_id, x in dict_with_blocks.items():
        min_line, max_line, level = x
        new_dict[level].append(
            {'block_id': block_id,
             'min_line': min_line,
             'max_line': max_line})
    return new_dict


def find_variable_declaration_in_ast(root,var_name):
    for ast, level in __traverse_ast(root):
        if (ast.type == 'variable_declarator'):
            var_name = ast.child_by_field_name('name')
            return ast, level


def find_variable_declaration_in_blocks(block_dict, start_point):
    for level, val in block_dict.items():
        for temp_node in val:
            if (start_point >= temp_node['min_line']) and (start_point <= temp_node['max_line']):
                return level, temp_node


if __name__ == '__main__':
    with open(
            r'D:\temp\temp_java_files\ClassFile_b88a1dd6690d51127c99ddfafe447c81589898cad0d4ab4274e32dd0f5577873.java') as f:
        # with open(r'D:\temp\temp_java_files\XMLConfPanel_b239893d29519f66c7a36066017b4a4192224e84d73a94eb650390eaa5bee8a7.java') as f:
        #     print(get_block_slices(f.read(), LANG_JAVA))

        # with open(r'D:\temp\temp_java_files\ClassFile_b88a1dd6690d51127c99ddfafe447c81589898cad0d4ab4274e32dd0f5577873.java') as f:
        # print(get_block_slices(f.read(), LANG_JAVA))
        text = f.read()
        # print(text.split('\n')[23])
        statements_by_block_id = __determine_unique_blocks_with_level(text, LANG_JAVA)
        ranges_by_block_id = {}
        block_id_by_ranges = defaultdict(list)
        for block_id, block_node in statements_by_block_id.items():
            # id_combinations = [c for c in itertools.combinations_with_replacement([idx for idx in range(len(statements))], 2)]
            lst = []
            for ids, level in block_node:
                lst.extend(list(range(ids.start_point[0], ids.end_point[0] + 1)))
            min_point = min(lst)
            max_point = max(lst)
            ranges_by_block_id[block_id] = (min_point, max_point, level)
            # block_id_by_ranges[(min_point, max_point)].append(block_id)

    tree_with_blocks_by_level = create_tree_by_level(ranges_by_block_id)
    slices = list(get_complete_computation_slices(text, LANG_JAVA))
    filtered_slices = []
    root = tree_sitter_ast(text, LANG_JAVA).root_node

    for function, variable, slices_by_var in slices:
        print(f'in func {function.name} for var {variable.name}')
        node, _ = find_variable_declaration_in_ast(root, variable.name)
        level, node = find_variable_declaration_in_blocks(tree_with_blocks_by_level, node.start_point[0])
        inside_block = True

        points = [current_slice.get_ranges() for current_slice in slices_by_var]
        for point in points:
            start_point = point[0][0]
            end_point = point[1][0]
            print(f'{start_point} {end_point}')
            if (start_point < node['min_line']) or end_point > node['max_line']:
                inside_block = False
                break

        if inside_block:
            filtered_slices.append((function, variable, slices_by_var))

    print(filtered_slices)

    # create_tree()

    # for block_id, item in ranges_by_block_id.items():

    # stats = __count_block_bounds(__generate_all_possible_opportunities(statements_by_block_id))
    # new_stats = []
    # for x, y in stats.items():
    #     sorted(list(itertools.chain(*y)), key=lambda x: (x[0][0] + 1, x[1][0]))
    #################################################################
#     slices = list(get_complete_computation_slices(text, LANG_JAVA))
#     total_ranges = []
#     slices_with_blocks = {}
#     for function, variable, slices_by_var in slices:
#         print(f'in func {function.name} for var {variable.name}')
#         list_slices = set()
#
#         for current_slice in slices_by_var:
#             temp_d = defaultdict(set)
#             for item in current_slice.get_ranges():
#                 start_point = item[0][0]
#                 end_point = item[1][0]
#                 print(f'{start_point} {end_point}')
#
#                 for block_id, ranges in ranges_by_block_id.items():
#                     if (start_point >= ranges[0]) and (end_point <= ranges[1]):
#                         # print(f'{start_point} {end_point} in block {block_id} {ranges}')
#                         temp_d[block_id].add((start_point, end_point))
#                         slices_with_blocks[variable.name] = temp_d
#                 # list_slices.add((item[0][0], item[1][0]))
#
#         total_ranges.append(list_slices)
#
# for var, dct in slices_with_blocks.items():
#     for block_id, lst in dct.items():
#         k = sorted(lst, key=lambda x: (x[0], x[1]))
        # print(f'{var} {block_id} {k}')

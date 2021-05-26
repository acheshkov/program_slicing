import operator
from collections import defaultdict
from itertools import combinations, combinations_with_replacement

import tree_sitter

from program_slicing.decomposition.slicing import __obtain_slicing_criteria, __obtain_common_boundary_blocks
from program_slicing.graph.cfg import ControlFlowGraph
from program_slicing.graph.manager import ProgramGraphsManager
from program_slicing.graph.parse import control_flow_graph, LANG_JAVA, program_dependence_graph
from operator import itemgetter, attrgetter, methodcaller
from program_slicing.graph.parse import tree_sitter_parsers
from program_slicing.graph.parse import cdg_java

parse_node_name = cdg_java.__parse_statement_name


def traverse_ast(root, level=0):
    for child in root.children:
        for ast_and_level in traverse_ast(child, level+1):
            yield ast_and_level
    yield root, level


def get_function_nodes(root):
    for ast, level in traverse_ast(root):
        if ast.type == "method_declaration" or ast.type == "constructor_declaration":
            yield ast


def get_block_nodes(root: tree_sitter.Node):
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


def generate_possible_opportunities(filename, function_name, start_line):
    with open(filename) as f:
        source_code = f.read()

    # manager = ProgramGraphsManager(source_code, LANG_JAVA)
    # cdg = manager.cdg
    # function_statements = cdg.get_entry_points()
    # edges = [x for x in cdg.edges]
    # for function_statement in function_statements:
    #     slicing_criteria = __obtain_slicing_criteria(cdg, function_statement)
    #     for variable_statement, seed_statements in slicing_criteria.items():
    #         common_boundary_blocks = __obtain_common_boundary_blocks(manager, seed_statements)
    #         print(str((variable_statement, common_boundary_blocks)))
    counter = 0;
    statements_by_block_id = {}
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

    statements_combinations_by_block_id = {}
    for block_id, statements in statements_by_block_id.items():
        id_combinations = [c for c in combinations_with_replacement([idx for idx in range(len(statements))], 2)]
        statements_combinations = [statements[ids[0]: ids[1]+1] for ids in id_combinations]
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
    # for node in traverse_ast(ast):
    #     body = node.child_by_field_name("body")
    #     if body is not None:
    #         ranges.append((body.start_point, body.end_point))

    # cfg: ControlFlowGraph = control_flow_graph(source_code, LANG_JAVA)
    # blocks = [(x, x.get_root().start_point[0]) for x in cfg]
    # sorted_blocks = sorted(blocks,  key=lambda x: x[1])
    # ignored_blocks = {'catch_formal_parameter', 'parenthesized_expression', 'enhanced_for_variable_declarator'}
    # blocks = []
    # for x, start_line in sorted_blocks:
    #     root = x.get_root()
    #     # if root.ast_node_type in ignored_blocks:
    #     #     continue
    #
    #     # if root.ast_node_type == 'local_variable_declaration':
    #     #     inner_stats = root.get_statements()
    #     #     if inner_stats[-1].ast_node_type == 'for_statement':
    #     #         continue
    #     print(f'block {root.start_point[0] + 1}, {root.end_point[0] + 1}, {root.ast_node_type} ')
    #     t_block = set()
    #     for j in x.get_statements():
    #         print(f'\tstat {j.start_point[0] + 1} {j.end_point[0] + 1}, {j.ast_node_type} ')
    #         t_block.add(j.end_point[0] + 1)
    #     blocks.append(range(root.start_point[0] + 1, root.end_point[0] + 1))
    # print(blocks)
    # for p in cfg.get_entry_points():
    #     # print(p.get_root().name, p.get_root().ast_node_type)
    #     stats = p.get_statements()
    #     for s in stats:
    #         if s.ast_node_type == 'block':
    #             print('################')
    #             for x in range(s.start_point[0], s.end_point[0]):
    #                 print(x + 1, s.statement_type)
    #             print('################')

    # pdg = program_dependence_graph(source_code, LANG_JAVA)
    # for p in pdg.get_entry_points():
    #     print(p.name, p.end_point[0])
    #     if p.ast_node_type == 'block':
    #         print('################')
    #         for x in range(p.start_point[0], p.end_point[0]):
    #             print(x + 1)
    #         print('################')


if __name__ == '__main__':
    generate_possible_opportunities(
        r'Logo.java',
        'all',
        13)

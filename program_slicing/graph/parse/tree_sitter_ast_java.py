__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/30'

from tree_sitter import Tree

from program_slicing.graph.parse import tree_sitter_parsers


def parse(source_code: str) -> Tree:
    """
    Parse the source code string into a Tree Sitter AST.
    :param source_code: string with the source code in it.
    :return: Tree Sitter AST.
    """
    supposed_ast = tree_sitter_parsers.java().parse(bytes(source_code, "utf8"))
    for node in supposed_ast.root_node.children:
        if node.type == "ERROR" and \
                node.next_named_sibling.type == "block" and \
                node.prev_named_sibling.type == "local_variable_declaration":
            return tree_sitter_parsers.java().parse(bytes(f'class C {{{source_code}}}', "utf8"))
    if {
        "class_declaration",
        "enum_declaration",
        "interface_declaration",
    }.intersection({node.type for node in supposed_ast.root_node.children}):
        return supposed_ast
    return tree_sitter_parsers.java().parse(bytes(f'class C {{ public void foo(){{{source_code}}} }}', "utf8"))

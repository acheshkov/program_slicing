__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/04/13'

import os
from pathlib import Path
from typing import Optional

from tree_sitter import Language, Parser, Node


project_path = Path(*Path(__file__).parts[:-4])

Language.build_library(
    # Store the library in the `build` directory
    os.path.join(project_path, "build", "languages.so"),

    # Include one or more languages
    [
        os.path.join(project_path, "vendor", "tree-sitter-java")
    ]
)


def java() -> Parser:
    parser = Parser()
    parser.set_language(Language(os.path.join(
        project_path, "build", "languages.so"), "java"))
    return parser


def node_name(source_code_bytes: bytes, ast: Node) -> Optional[str]:
    """
    Parse a Tree Sitter AST Node's name using the original source code bytes.
    :param source_code_bytes: source code bytes.
    :param ast: Tree Sitter AST Node.
    :return: string with the node's name if it exists, none otherwise.
    """
    if ast.type in {"variable_declarator", "formal_parameter"}:
        return node_name(source_code_bytes, ast.child_by_field_name("name"))
    elif ast.type == "assignment_expression":
        return node_name(source_code_bytes, ast.child_by_field_name("left"))
    elif ast.type == "update_expression":
        expr_ast = ast.children[0]
        expr_ast = expr_ast if expr_ast.next_named_sibling is None else expr_ast.next_named_sibling
        return node_name(source_code_bytes, expr_ast)
    elif ast.type == "catch_formal_parameter":
        return node_name(source_code_bytes, ast.child_by_field_name("name"))
    elif ast.type == "break_statement":
        identifier_ast = ast.children[0].next_named_sibling
        return None if identifier_ast is None else node_name(source_code_bytes, identifier_ast)
    elif ast.type == "continue_statement":
        identifier_ast = ast.children[0].next_named_sibling
        return None if identifier_ast is None else node_name(source_code_bytes, identifier_ast)
    elif ast.type == "labeled_statement":
        return source_code_bytes[ast.children[0].start_byte: ast.children[0].end_byte].decode("utf8")
    elif ast.parent is not None and ast.parent.type == "labeled_statement":
        return node_name(source_code_bytes, ast.parent)
    elif ast.start_point[0] == ast.end_point[0]:
        return source_code_bytes[ast.start_byte: ast.end_byte].decode("utf8")
    return None

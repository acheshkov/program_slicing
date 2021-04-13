__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/04/13'

import os

from tree_sitter import Language, Parser


Language.build_library(
    # Store the library in the `build` directory
    os.path.join("..", "build", "languages.so"),

    # Include one or more languages
    [
        os.path.join("..", "vendor", "tree-sitter-java")
    ]
)


def java() -> Parser:
    parser = Parser()
    parser.set_language(Language(os.path.join("..", "build", "languages.so"), "java"))
    return parser

__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/04/13'

import os
from pathlib import Path

from tree_sitter import Language, Parser


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

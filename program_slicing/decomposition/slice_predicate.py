__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/06/03'

from typing import Set

from program_slicing.decomposition.program_slice import ProgramSlice
from program_slicing.graph.statement import StatementType
from program_slicing.graph.point import Point
from program_slicing.graph.manager import ProgramGraphsManager
from program_slicing.graph.parse import parse
from program_slicing.graph.parse.tree_sitter_parsers import node_name


class SlicePredicate:

    def __init__(
            self,
            min_amount_of_lines: int = None,
            max_amount_of_lines: int = None,
            lang_to_check_parsing: str = None,
            forbidden_words: Set[str] = None,
            has_returnable_variable: bool = None):
        self.__min_amount_of_lines = min_amount_of_lines
        self.__max_amount_of_lines = max_amount_of_lines
        self.__lang_to_check_parsing = lang_to_check_parsing
        self.__forbidden_words = forbidden_words
        self.__has_returnable_variable = has_returnable_variable
        self.__checkers = [
            self.__check_min_amount_of_lines,
            self.__check_max_amount_of_lines,
            self.__check_parsing,
            self.__check_has_returnable_variable,
            self.__check_forbidden_words
        ]
        self.__program_slice = None
        self.__manager = None

    def __call__(self, program_slice: ProgramSlice) -> bool:
        if program_slice is None:
            raise ValueError("Program slice has to be defined")
        self.__program_slice = program_slice
        for checker in self.__checkers:
            if not checker():
                return False
        return True

    def __check_min_amount_of_lines(self) -> bool:
        if self.__min_amount_of_lines is None:
            return True
        if len(self.__program_slice.lines) < self.__min_amount_of_lines:
            return False
        return True

    def __check_max_amount_of_lines(self) -> bool:
        if self.__max_amount_of_lines is None:
            return True
        if len(self.__program_slice.lines) > self.__max_amount_of_lines:
            return False
        return True

    def __check_parsing(self) -> bool:
        if self.__lang_to_check_parsing is None:
            return True
        code_bytes = bytes(self.__program_slice.code, "utf-8")
        self.__manager = ProgramGraphsManager(self.__program_slice.code, self.__lang_to_check_parsing)
        # TODO: manager may contain ast info, no need to parse it twice
        ast = parse.tree_sitter_ast(self.__program_slice.code, self.__lang_to_check_parsing).root_node

        def traverse(root):
            yield root
            if root.children:
                for child in root.children:
                    for result in traverse(child):
                        yield result
        for node in traverse(ast):
            if node.type == "ERROR":
                return False
            elif node.type == "type_identifier":
                # code "else a = 0;" in tree sitter java parser doesn't create an ERROR node,
                # it wrongly parse 'else' as a type_identifier,
                # that's why we need this additional check;
                # this code may be removed if tree sitter will fix this issue
                if node_name(code_bytes, node) == "else":
                    return False
        return self.__check_no_broken_goto()

    def __check_no_broken_goto(self) -> bool:
        cdg = self.__manager.get_control_dependence_graph()
        for statement in cdg:
            if statement.statement_type == StatementType.GOTO:
                if statement not in cdg.control_flow or not cdg.control_flow[statement]:
                    return False
        return True

    def __check_has_returnable_variable(self) -> bool:
        if self.__has_returnable_variable is None or self.__manager is None:
            return True
        for statement in self.__manager.get_control_dependence_graph():
            if statement.statement_type == StatementType.VARIABLE:
                scope = self.__manager.get_scope_statement(statement)
                lines = self.__program_slice.lines
                if (scope.statement_type == StatementType.SCOPE or scope.statement_type == StatementType.FUNCTION) and \
                        scope.start_point == Point(0, 0) and scope.end_point == Point(len(lines) - 1, len(lines[-1])):
                    return True
        return False

    def __check_forbidden_words(self) -> bool:
        if self.__forbidden_words is None:
            return True
        code = self.__program_slice.code
        for forbidden_word in self.__forbidden_words:
            if forbidden_word in code:
                return False
        return True


def check_slice(
        program_slice: ProgramSlice,
        min_amount_of_lines: int = None,
        max_amount_of_lines: int = None,
        lang_to_check_parsing: str = None,
        has_returnable_variable: bool = None) -> bool:
    """
    Check a ProgramSlice if it matches specified conditions.
    :param program_slice: slice that should to be checked.
    :param min_amount_of_lines: minimal acceptable amount of lines.
    :param max_amount_of_lines: maximal acceptable amount of lines.
    :param lang_to_check_parsing: language in which slice should to be compilable.
    :param has_returnable_variable: slice should to have a declaration of variable that may be returned if needed.
    Flag is ignored if lang_to_check_parsing is not specified.
    :return: True if slice matches specified conditions.
    """
    return SlicePredicate(
        min_amount_of_lines=min_amount_of_lines,
        max_amount_of_lines=max_amount_of_lines,
        lang_to_check_parsing=lang_to_check_parsing,
        has_returnable_variable=has_returnable_variable
    )(program_slice)

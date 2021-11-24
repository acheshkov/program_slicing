__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/06/03'

from typing import Set, Optional, Iterable, Tuple

import networkx

from program_slicing.decomposition.program_slice import ProgramSlice
from program_slicing.graph.manager import ProgramGraphsManager
from program_slicing.graph.parse import parse
from program_slicing.graph.parse import Lang
from program_slicing.graph.parse.tree_sitter_parsers import node_name
from program_slicing.graph.statement import Statement
from program_slicing.graph.statement import StatementType
from program_slicing.graph.point import Point


class SlicePredicate:

    def __init__(
            self,
            min_amount_of_lines: int = None,
            max_amount_of_lines: int = None,
            min_amount_of_statements: int = None,
            max_amount_of_statements: int = None,
            min_amount_of_exit_statements: int = None,
            max_amount_of_exit_statements: int = None,
            min_percentage_of_statements: float = None,
            max_percentage_of_statements: float = None,
            min_percentage_of_lines: float = None,
            max_percentage_of_lines: float = None,
            lines_are_full: bool = None,
            lang_to_check_parsing: Lang = None,
            has_returnable_variable: bool = None,
            is_whole_scope: bool = None,
            cause_code_duplication: bool = None,
            forbidden_words: Set[str] = None):
        self.__min_amount_of_statements = min_amount_of_statements
        self.__max_amount_of_statements = max_amount_of_statements
        self.__min_amount_of_lines = min_amount_of_lines
        self.__max_amount_of_lines = max_amount_of_lines
        self.__min_amount_of_exit_statements = min_amount_of_exit_statements
        self.__max_amount_of_exit_statements = max_amount_of_exit_statements
        self.__min_percentage_of_statements = min_percentage_of_statements
        self.__max_percentage_of_statements = max_percentage_of_statements
        self.__min_percentage_of_lines = min_percentage_of_lines
        self.__max_percentage_of_lines = max_percentage_of_lines
        self.__lines_are_full = lines_are_full
        self.__lang_to_check_parsing = lang_to_check_parsing
        self.__has_returnable_variable = has_returnable_variable
        self.__is_whole_scope = is_whole_scope
        self.__cause_code_duplication = cause_code_duplication
        self.__forbidden_words = forbidden_words
        self.__statements_checkers = [
            self.__check_min_amount_of_statements,
            self.__check_max_amount_of_statements,
            self.__check_cause_code_duplication,
            self.__check_min_amount_of_exit_statements,
            self.__check_max_amount_of_exit_statements,
            self.__check_min_percentage_of_statements,
            self.__check_max_percentage_of_statements,
            self.__check_is_whole_scope,
            self.__check_has_returnable_variable
        ]
        self.__checkers = [
            self.__check_min_amount_of_lines,
            self.__check_max_amount_of_lines,
            self.__check_min_percentage_of_lines,
            self.__check_max_percentage_of_lines,
            self.__check_lines_are_full,
            self.__check_forbidden_words,
            self.__check_parsing
        ]
        self.__program_slice = None
        self.__statements = None
        self.__general_statements = None
        self.__bounds = None
        self.__generated_manager = None

    def __call__(self, program_slice: ProgramSlice, **kwargs) -> bool:
        if program_slice is None:
            raise ValueError("Program slice has to be defined")
        self.__program_slice = program_slice
        result = True
        if self.__statements is None:
            general_statements = self.__program_slice.general_statements
            if not general_statements and self.__program_slice.ranges:
                generated_manager = self.__get_generated_manager()
                if generated_manager:
                    general_statements = {statement for statement in generated_manager.general_statements}
            result = self.check_statements(general_statements, statements=program_slice.statements, **kwargs)
        if result:
            for checker in self.__checkers:
                if not checker(**kwargs):
                    result = False
                    break
        self.__program_slice = None
        self.__statements = None
        self.__general_statements = None
        self.__bounds = None
        self.__generated_manager = None
        return result

    @property
    def min_amount_of_lines(self) -> int:
        return self.__min_amount_of_lines

    @property
    def max_amount_of_lines(self) -> int:
        return self.__max_amount_of_lines

    @property
    def min_amount_of_statements(self) -> int:
        return self.__min_amount_of_statements

    @property
    def max_amount_of_statements(self) -> int:
        return self.__max_amount_of_statements

    @property
    def min_amount_of_exit_statements(self) -> int:
        return self.__min_amount_of_exit_statements

    @property
    def max_amount_of_exit_statements(self) -> int:
        return self.__max_amount_of_exit_statements

    @property
    def min_percentage_of_statements(self) -> float:
        return self.__min_percentage_of_statements

    @property
    def max_percentage_of_statements(self) -> float:
        return self.__max_percentage_of_statements

    @property
    def min_percentage_of_lines(self) -> float:
        return self.__min_percentage_of_lines

    @property
    def max_percentage_of_lines(self) -> float:
        return self.__max_percentage_of_lines

    @property
    def lines_are_full(self) -> bool:
        return self.__lines_are_full

    @property
    def lang_to_check_parsing(self) -> Lang:
        return self.__lang_to_check_parsing

    @property
    def has_returnable_variable(self) -> bool:
        return self.__has_returnable_variable

    @property
    def is_whole_scope(self) -> bool:
        return self.__is_whole_scope

    @property
    def cause_code_duplication(self) -> bool:
        return self.__cause_code_duplication

    @property
    def forbidden_words(self) -> Set[str]:
        return self.__forbidden_words

    def check_statements(
            self,
            general_statements: Iterable[Statement],
            statements: Iterable[Statement] = None,
            **kwargs) -> bool:
        self.__generated_manager = None
        self.__bounds = None
        self.__general_statements = general_statements
        if statements is None:
            self.__statements = self.__general_statements
        else:
            self.__statements = statements
        for checker in self.__statements_checkers:
            if self.__general_statements is None or not checker(**kwargs):
                return False
        return True

    def __check_is_whole_scope(self, context: ProgramGraphsManager = None, **kwargs) -> bool:
        if self.__is_whole_scope is None:
            return True
        if context is None:
            context = None if self.__program_slice is None else self.__program_slice.context
            if context is None:
                raise ValueError("context has to be specified to check if slice is a whole scope")
        if not context.scope_statements:
            return not self.__is_whole_scope
        bounds = self.__get_bounds()
        if bounds is None:
            return not self.is_whole_scope
        start_point, end_point = bounds
        scopes_points = {(x.start_point, x.end_point) for x in context.scope_statements}
        if (start_point, end_point) in scopes_points:
            return self.__is_whole_scope
        return not self.__is_whole_scope

    def __check_cause_code_duplication(self, context: ProgramGraphsManager = None, **kwargs) -> bool:
        if self.__cause_code_duplication is None:
            return True
        if context is None:
            context = None if self.__program_slice is None else self.__program_slice.context
            if context is None:
                raise ValueError("context has to be specified to check if slice cause code duplication")
        affecting_statements = context.get_affecting_statements(self.__statements)
        if len(context.get_changed_variables_statements(affecting_statements)) > 1:
            return self.__cause_code_duplication
        if self.__contain_redundant_statements(context, self.__statements):
            return self.__cause_code_duplication
        if self.__affects_inner_statements(context, affecting_statements):
            return self.__cause_code_duplication
        controlled_statements = set()
        for statement in sorted(self.__statements, key=lambda x: (x.start_point, -x.end_point)):
            if statement in controlled_statements:
                continue
            controlled_statements.update(networkx.descendants(context.control_dependence_graph, statement))
        if any(statement not in self.__statements for statement in controlled_statements):
            return self.__cause_code_duplication
        return not self.__cause_code_duplication

    def __check_min_amount_of_exit_statements(self, context: ProgramGraphsManager = None, **kwargs) -> bool:
        if self.__min_amount_of_exit_statements is None:
            return True
        if context is None:
            context = None if self.__program_slice is None else self.__program_slice.context
            if context is None:
                raise ValueError("context has to be specified to check amount of exit statements")
        if len(context.get_exit_statements(self.__statements)) < self.__min_amount_of_exit_statements:
            return False
        return True

    def __check_max_amount_of_exit_statements(self, context: ProgramGraphsManager = None, **kwargs) -> bool:
        if self.__max_amount_of_exit_statements is None:
            return True
        if context is None:
            context = None if self.__program_slice is None else self.__program_slice.context
            if context is None:
                raise ValueError("context has to be specified to check amount of exit statements")
        if len(context.get_exit_statements(self.__statements)) > self.__max_amount_of_exit_statements:
            return False
        return True

    def __check_min_amount_of_statements(self, **kwargs) -> bool:
        if self.__min_amount_of_statements is None:
            return True
        if len(self.__general_statements) < self.__min_amount_of_statements:
            return False
        return True

    def __check_max_amount_of_statements(self, **kwargs) -> bool:
        if self.__max_amount_of_statements is None:
            return True
        if len(self.__general_statements) > self.__max_amount_of_statements:
            return False
        return True

    def __check_min_percentage_of_statements(self, context: ProgramGraphsManager = None, **kwargs) -> bool:
        if self.__min_percentage_of_statements is None:
            return True
        if context is None:
            context = None if self.__program_slice is None else self.__program_slice.context
            if context is None:
                raise ValueError("context has to be specified to check percentage of statements")
        if len(self.__general_statements) / self.__get_number_of_statements(context) < \
                self.__min_percentage_of_statements:
            return False
        return True

    def __check_max_percentage_of_statements(self, context: ProgramGraphsManager = None, **kwargs) -> bool:
        if self.__max_percentage_of_statements is None:
            return True
        if context is None:
            context = None if self.__program_slice is None else self.__program_slice.context
            if context is None:
                raise ValueError("context has to be specified to check percentage of statements")
        if len(self.__general_statements) / self.__get_number_of_statements(context) > \
                self.__max_percentage_of_statements:
            return False
        return True

    def __check_min_amount_of_lines(self, **kwargs) -> bool:
        if self.__min_amount_of_lines is None:
            return True
        if len(self.__program_slice.lines) < self.__min_amount_of_lines:
            return False
        return True

    def __check_max_amount_of_lines(self, **kwargs) -> bool:
        if self.__max_amount_of_lines is None:
            return True
        if len(self.__program_slice.lines) > self.__max_amount_of_lines:
            return False
        return True

    def __check_min_percentage_of_lines(self, context: ProgramGraphsManager = None, **kwargs) -> bool:
        if self.__min_percentage_of_lines is None:
            return True
        if context is None:
            context = self.__program_slice.context
            if context is None:
                raise ValueError("context has to be specified to check percentage of lines")
        if len(self.__program_slice.lines) / self.__get_number_of_lines(context) < self.__min_percentage_of_lines:
            return False
        return True

    def __check_max_percentage_of_lines(self, context: ProgramGraphsManager = None, **kwargs) -> bool:
        if self.__max_percentage_of_lines is None:
            return True
        if context is None:
            context = self.__program_slice.context
            if context is None:
                raise ValueError("context has to be specified to check percentage of lines")
        if len(self.__program_slice.lines) / self.__get_number_of_lines(context) > self.__max_percentage_of_lines:
            return False
        return True

    def __check_lines_are_full(self, **kwargs) -> bool:
        if self.__lines_are_full is None:
            return True
        source_lines = self.__program_slice.source_lines
        for current_range in self.__program_slice.ranges:
            current_line_bounds = \
                source_lines[current_range[0].line_number][:current_range[0].column_number] + \
                source_lines[current_range[1].line_number][current_range[1].column_number:]
            contain_commented_part = False
            for char in current_line_bounds:
                if char == "/":
                    if contain_commented_part:
                        break
                    contain_commented_part = True
                    continue
                if contain_commented_part:
                    return not self.__lines_are_full
                if char != ' ' and char != '\t' and char != '\r':
                    return not self.__lines_are_full
        return self.__lines_are_full

    def __check_parsing(self, **kwargs) -> bool:
        if self.__lang_to_check_parsing is None:
            return True
        code_bytes = bytes(self.__program_slice.code, "utf-8")
        manager = self.__get_generated_manager()
        # TODO: manager may contain ast info, no need to parse it twice
        ast = parse.tree_sitter_ast(self.__program_slice.code, self.__lang_to_check_parsing).root_node
        for node in SlicePredicate.__traverse(ast):
            if node.type == "ERROR":
                return False
            elif node.type == "type_identifier":
                # code "else a = 0;" in tree sitter java parser doesn't create an ERROR node,
                # it wrongly parse 'else' as a type_identifier,
                # that's why we need this additional check;
                # this code may be removed if tree sitter will fix this issue
                if node_name(code_bytes, node) == "else":
                    return False
        cdg = manager.control_dependence_graph
        for statement in cdg:
            if statement.statement_type == StatementType.GOTO:
                if not cdg.control_flow.get(statement, None):
                    return False
        return True

    def __check_has_returnable_variable(self, context: ProgramGraphsManager = None, **kwargs) -> bool:
        if self.__has_returnable_variable is None:
            return True
        if context is None:
            context = None if self.__program_slice is None else self.__program_slice.context
            if context is None:
                context = self.__get_generated_manager()
                if context is None:
                    raise ValueError("context has to be specified to check if slice has returnable variable")
                self.__statements = context.sorted_statements
                self.__general_statements = context.general_statements
        bounds = self.__get_bounds()
        if bounds is None:
            return not self.__has_returnable_variable
        start_point, end_point = bounds
        for statement in self.__statements:
            if statement.statement_type == StatementType.VARIABLE:
                variable = self.__program_slice.variable if self.__program_slice else kwargs.get("variable", None)
                if variable and variable.name != statement.name:
                    continue
                scope = context.get_scope_statement(statement)
                if scope is None or \
                        (scope.statement_type in {StatementType.SCOPE, StatementType.FUNCTION}) and \
                        scope.start_point <= start_point and scope.end_point >= end_point:
                    return self.__has_returnable_variable
        return not self.__has_returnable_variable

    def __check_forbidden_words(self, **kwargs) -> bool:
        if self.__forbidden_words is None:
            return True
        code = self.__program_slice.code
        for forbidden_word in self.__forbidden_words:
            if forbidden_word in code:
                return False
        return True

    def __get_number_of_lines(self, context: ProgramGraphsManager) -> int:
        bounds = self.__get_bounds()
        if bounds is None:
            return 1
        start_point, end_point = bounds
        slice_function = context.get_function_statement_by_range(start_point, end_point)
        if slice_function is None:
            return 1
        if len(context.get_statements_in_scope(slice_function)) > 1:
            return slice_function.end_point.line_number - slice_function.start_point.line_number + 1
        return max(1, (slice_function.end_point.line_number - slice_function.start_point.line_number - 1))
        # return 1 if slice_function is None else max(1, len(context.get_statement_line_numbers(slice_function)))

    def __get_number_of_statements(self, context: ProgramGraphsManager) -> int:
        bounds = self.__get_bounds()
        if bounds is None:
            return 1
        start_point, end_point = bounds
        slice_function = context.get_function_statement_by_range(start_point, end_point)
        statements_in_function = set() if slice_function is None else context.get_statements_in_range(
            slice_function.start_point,
            slice_function.end_point)
        return max(1, len([
            statement for statement in context.general_statements if statement in statements_in_function
        ]))

    def __get_generated_manager(self) -> Optional[ProgramGraphsManager]:
        if self.__generated_manager is None:
            if self.__lang_to_check_parsing is not None:
                self.__generated_manager = ProgramGraphsManager(self.__program_slice.code, self.__lang_to_check_parsing)
        return self.__generated_manager

    def __get_bounds(self) -> Tuple[Point, Point]:
        if self.__bounds is not None:
            return self.__bounds
        if self.__program_slice:
            self.__bounds = (self.__program_slice.ranges[0][0], self.__program_slice.ranges[-1][1])
        elif self.__general_statements:
            self.__bounds = (
                min(s.start_point for s in self.__general_statements),
                max(s.end_point for s in self.__general_statements)
            )
        return self.__bounds

    def __contain_redundant_statements(self, context: ProgramGraphsManager, statements: Set[Statement]) -> bool:
        """
        Check if the given set of Statements contain part of some construction not fully included in the given set.
        :param context: a ProgramGraphsManager that defines context of the given ProgramSlice.
        :param statements: set of Statements for which check on redundant Statements presence should to be done.
        :return: True if the given set contains redundant Statements.
        """
        for statement in statements:
            if statement.ast_node_type == "else" or statement.ast_node_type == "catch_clause":
                for predecessor in context.control_dependence_graph.predecessors(statement):
                    if predecessor not in statements:
                        return True
            elif statement.ast_node_type == "finally_clause" and \
                    self.__is_redundant_finally(context, statement, statements):
                return True
            elif statement.ast_node_type == "if_statement" and \
                    self.__is_redundant_if(context, statement, statements):
                return True
        return False

    def __affects_inner_statements(self, context: ProgramGraphsManager, affecting_statements: Set[Statement]) -> bool:
        if len(affecting_statements) == 0:
            return False
        start_point = min(statement.start_point for statement in affecting_statements)
        end_point = max(statement.end_point for statement in affecting_statements)
        for affecting_statement in affecting_statements:
            if any(
                    s not in self.__statements and s.end_point < end_point and s.start_point > start_point
                    for s in context.data_dependence_graph.successors(affecting_statement)):
                return True
        return False

    @staticmethod
    def __is_redundant_finally(context: ProgramGraphsManager, statement: Statement, statements: Set[Statement]) -> bool:
        finally_block = context.get_basic_block(statement)
        if finally_block is None:
            return True
        for predecessor_block in context.control_flow_graph.predecessors(finally_block):
            if predecessor_block.statements and predecessor_block.statements[-1] not in statements:
                return True
        return False

    @staticmethod
    def __is_redundant_if(context: ProgramGraphsManager, statement: Statement, statements: Set[Statement]) -> bool:
        if statement in context.control_dependence_graph.control_flow:
            for successor in context.control_dependence_graph.control_flow[statement]:
                if successor.ast_node_type == "else" and successor not in statements:
                    return True
        return False

    @staticmethod
    def __traverse(root):
        yield root
        if root.children:
            for child in root.children:
                for result in SlicePredicate.__traverse(child):
                    yield result


def check_slice(
        program_slice: ProgramSlice,
        min_amount_of_lines: int = None,
        max_amount_of_lines: int = None,
        min_amount_of_statements: int = None,
        max_amount_of_statements: int = None,
        min_amount_of_exit_statements: int = None,
        max_amount_of_exit_statements: int = None,
        min_percentage_of_statements: float = None,
        max_percentage_of_statements: float = None,
        min_percentage_of_lines: float = None,
        max_percentage_of_lines: float = None,
        lines_are_full: bool = None,
        lang_to_check_parsing: Lang = None,
        has_returnable_variable: bool = None,
        is_whole_scope: bool = None,
        cause_code_duplication: bool = None,
        forbidden_words: Set[str] = None,
        context: ProgramGraphsManager = None) -> bool:
    """
    Check a ProgramSlice if it matches specified conditions.
    :param program_slice: slice that should to be checked.
    :param min_amount_of_lines: minimal acceptable amount of lines.
    :param max_amount_of_lines: maximal acceptable amount of lines.
    :param min_amount_of_statements: minimal acceptable amount of Statements.
    Will raise Exception if lang_to_check_parsing is not specified.
    :param max_amount_of_statements: maximal acceptable amount of Statements.
    Will raise Exception if lang_to_check_parsing is not specified.
    :param min_amount_of_exit_statements: minimal acceptable amount of exit Statements.
    :param max_amount_of_exit_statements: maximal acceptable amount of exit Statements.
    :param min_percentage_of_statements: minimal acceptable share of Statements (float number [0-1]).
    May raise Exception if context is not specified.
    :param max_percentage_of_statements: maximal acceptable share of Statements (float number [0-1]).
    May raise Exception if context is not specified.
    :param min_percentage_of_lines: minimal acceptable share of lines (float number [0-1]).
    May raise Exception if context is not specified.
    :param max_percentage_of_lines: maximal acceptable share of lines (float number [0-1]).
    May raise Exception if context is not specified.
    :param lines_are_full: check if the slice contains only entire lines.
    :param lang_to_check_parsing: language in which slice should to be compilable.
    :param has_returnable_variable: slice should to have a declaration of variable that may be returned if needed.
    May raise Exception if lang_to_check_parsing is not specified.
    :param is_whole_scope: slice is a whole scope if True and is not a whole scope if False.
    May raise Exception if context or at least lang_to_check_parsing are not specified.
    :param cause_code_duplication: slice's extraction should cause code duplication if True and should not if False.
    :param forbidden_words: a set of substrings that shouldn't be found in a slice code.
    :param context: a ProgramGraphsManager that defines context of the given ProgramSlice.
    :return: True if slice matches specified conditions.
    """
    return SlicePredicate(
        min_amount_of_lines=min_amount_of_lines,
        max_amount_of_lines=max_amount_of_lines,
        min_amount_of_statements=min_amount_of_statements,
        max_amount_of_statements=max_amount_of_statements,
        min_amount_of_exit_statements=min_amount_of_exit_statements,
        max_amount_of_exit_statements=max_amount_of_exit_statements,
        min_percentage_of_statements=min_percentage_of_statements,
        max_percentage_of_statements=max_percentage_of_statements,
        min_percentage_of_lines=min_percentage_of_lines,
        max_percentage_of_lines=max_percentage_of_lines,
        lines_are_full=lines_are_full,
        lang_to_check_parsing=lang_to_check_parsing,
        has_returnable_variable=has_returnable_variable,
        is_whole_scope=is_whole_scope,
        cause_code_duplication=cause_code_duplication,
        forbidden_words=forbidden_words
    )(program_slice, context=context)

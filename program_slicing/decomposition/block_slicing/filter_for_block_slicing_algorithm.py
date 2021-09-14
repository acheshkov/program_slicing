from program_slicing.decomposition.program_slice import ProgramSlice
from program_slicing.graph.cdg import ControlDependenceGraph
from program_slicing.graph.manager import ProgramGraphsManager
from program_slicing.graph.parse import parse, control_flow_graph
from program_slicing.graph.parse.tree_sitter_parsers import node_name
from program_slicing.graph.statement import StatementType

from program_slicing.graph.cdg import ControlDependenceGraph
from program_slicing.graph.parse import control_dependence_graph, LANG_JAVA


def check_all_lines_are_full(program_slice: ProgramSlice) -> bool:
    """
    Check if the slice contains only entire lines.

    :return:
    """
    source_lines = program_slice.source_lines
    for current_range in program_slice.ranges:
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
                return False
            if char != ' ' and char != '\t' and char != '\r':
                return False
    return True


def check_parsing(program_slice: ProgramSlice, lang: str) -> bool:
    code_bytes = bytes(program_slice.code, "utf-8")
    # TODO: manager may contain ast info, no need to parse it twice
    ast = parse.tree_sitter_ast(program_slice.code, lang).root_node

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

    cdg = control_dependence_graph(program_slice.code, lang)
    return check_no_broken_goto(cdg)


def check_no_broken_goto(cdg) -> bool:
    for statement in cdg:
        if statement.statement_type == StatementType.GOTO:
            if not cdg.control_flow.get(statement, None):
                return False
    return True


# def check_min_amount_of_statements(program_slice: ProgramSlice, min_amount_of_statements) -> bool:
#     return len(self.__manager.general_statements) < min_amount_of_statements


def check_min_amount_of_lines(program_slice: ProgramSlice, min_amount_of_lines) -> bool:
    return len(program_slice.lines) < min_amount_of_lines

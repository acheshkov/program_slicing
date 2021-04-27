__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/30'

from typing import List, Tuple, Callable, Optional

from tree_sitter import Node

from program_slicing.graph.parse import tree_sitter_parsers
from program_slicing.graph.cdg import ControlDependenceGraph
from program_slicing.graph.statement import Statement, \
    STATEMENT_TYPE_FUNCTION, \
    STATEMENT_TYPE_VARIABLE, \
    STATEMENT_TYPE_ASSIGNMENT, \
    STATEMENT_TYPE_CALL, \
    STATEMENT_TYPE_STATEMENTS, \
    STATEMENT_TYPE_BRANCH, \
    STATEMENT_TYPE_LOOP, \
    STATEMENT_TYPE_GOTO, \
    STATEMENT_TYPE_OBJECT, \
    STATEMENT_TYPE_EXIT


parser = tree_sitter_parsers.java()


def __handle_statement(
        statement: Statement,
        source_code_bytes,
        ast: Node,
        cdg: ControlDependenceGraph,
        break_statements: List[Statement] = None,
        continue_statements: List[Statement] = None) -> Tuple[List[Statement], List[Statement]]:
    siblings = [statement]
    entry_points = [statement]
    for child in ast.children:
        siblings += __parse(
            source_code_bytes,
            child,
            cdg,
            entry_points,
            break_statements=break_statements,
            continue_statements=continue_statements)
    return siblings, entry_points


def __handle_method_declaration(
        statement: Statement,
        source_code_bytes,
        ast: Node,
        cdg: ControlDependenceGraph,
        break_statements: List[Statement] = None,
        continue_statements: List[Statement] = None) -> Tuple[List[Statement], List[Statement]]:
    cdg.add_entry_point(statement)
    siblings = [statement]
    entry_points = [statement]
    children = __parse(
        source_code_bytes,
        ast.child_by_field_name("body"),
        cdg,
        entry_points,
        break_statements=break_statements,
        continue_statements=continue_statements)
    for child in children:
        cdg.add_edge(statement, child)
    return siblings, entry_points


def __handle_if(
        statement: Statement,
        source_code_bytes,
        ast: Node,
        cdg: ControlDependenceGraph,
        break_statements: List[Statement] = None,
        continue_statements: List[Statement] = None) -> Tuple[List[Statement], List[Statement]]:
    entry_points = []
    siblings = __parse(
        source_code_bytes,
        ast.child_by_field_name("condition"),
        cdg,
        entry_points,
        break_statements=break_statements,
        continue_statements=continue_statements)
    siblings.append(statement)
    __route_control_flow(entry_points, statement, cdg)
    entry_points = [statement]
    consequence = __parse(
        source_code_bytes,
        ast.child_by_field_name("consequence"),
        cdg,
        entry_points,
        break_statements=break_statements,
        continue_statements=continue_statements)
    for child in consequence:
        cdg.add_edge(statement, child)
    alternative_ast = ast.child_by_field_name("alternative")
    alternative_entry_points = [statement]
    if alternative_ast is not None:
        alternative = __parse(
            source_code_bytes,
            alternative_ast,
            cdg,
            alternative_entry_points,
            break_statements=break_statements,
            continue_statements=continue_statements)
        for child in alternative:
            cdg.add_edge(statement, child)

    return siblings, entry_points + alternative_entry_points


def __handle_try(
        statement: Statement,
        source_code_bytes,
        ast: Node,
        cdg: ControlDependenceGraph,
        break_statements: List[Statement] = None,
        continue_statements: List[Statement] = None) -> Tuple[List[Statement], List[Statement]]:
    siblings = []
    entry_points = []
    resources_ast = ast.child_by_field_name("resources")
    if resources_ast is not None:
        siblings += __parse(
            source_code_bytes,
            resources_ast,
            cdg,
            entry_points,
            break_statements=break_statements,
            continue_statements=continue_statements)
    body_ast = ast.child_by_field_name("body")
    siblings += __parse(
        source_code_bytes,
        body_ast,
        cdg,
        entry_points,
        break_statements=break_statements,
        continue_statements=continue_statements)
    siblings.append(statement)
    __route_control_flow(entry_points, statement, cdg)
    exit_points = [statement]
    entry_points = [statement]
    clause_ast = body_ast.next_named_sibling
    while clause_ast is not None and clause_ast.type != "finally_clause":
        clause = __parse(
            source_code_bytes,
            clause_ast,
            cdg,
            entry_points,
            break_statements=break_statements,
            continue_statements=continue_statements)
        for child in clause:
            cdg.add_edge(statement, child)
        statement = clause[-1]
        exit_points += entry_points
        entry_points = [statement]
        clause_ast = clause_ast.next_named_sibling
    if exit_points != entry_points:
        exit_points += entry_points
    if clause_ast is not None:
        siblings += __parse(
            source_code_bytes,
            clause_ast,
            cdg,
            exit_points,
            break_statements=break_statements,
            continue_statements=continue_statements)
    return siblings, exit_points


def __handle_catch(
        statement: Statement,
        source_code_bytes,
        ast: Node,
        cdg: ControlDependenceGraph,
        break_statements: List[Statement] = None,
        continue_statements: List[Statement] = None) -> Tuple[List[Statement], List[Statement]]:
    entry_points = []
    siblings = __parse(
        source_code_bytes,
        ast.child_by_field_name("body").prev_named_sibling,
        cdg,
        entry_points,
        break_statements=break_statements,
        continue_statements=continue_statements)
    siblings.append(statement)
    __route_control_flow(entry_points, statement, cdg)
    entry_points = [statement]
    body = __parse(
        source_code_bytes,
        ast.child_by_field_name("body"),
        cdg,
        entry_points,
        break_statements=break_statements,
        continue_statements=continue_statements)
    for child in body:
        cdg.add_edge(statement, child)
    return siblings, entry_points


def __handle_for(
        statement: Statement,
        source_code_bytes,
        ast: Node,
        cdg: ControlDependenceGraph,
        break_statements: List[Statement] = None,
        continue_statements: List[Statement] = None) -> Tuple[List[Statement], List[Statement]]:
    siblings = []
    entry_points = []
    init_ast = ast.child_by_field_name("init")
    if init_ast is not None:
        siblings += __parse(
            source_code_bytes,
            init_ast,
            cdg,
            entry_points,
            break_statements=break_statements,
            continue_statements=continue_statements)
    condition = __parse(
        source_code_bytes,
        ast.child_by_field_name("condition"),
        cdg,
        entry_points,
        break_statements=break_statements,
        continue_statements=continue_statements)
    siblings += condition
    siblings.append(statement)
    __route_control_flow(entry_points, statement, cdg)
    entry_points = [statement]
    local_break_statements = []
    local_continue_statements = []
    body = __parse(
        source_code_bytes,
        ast.child_by_field_name("body"),
        cdg,
        entry_points,
        break_statements=local_break_statements,
        continue_statements=local_continue_statements)
    update_ast = ast.child_by_field_name("update")
    if update_ast is not None:
        update = __parse(
            source_code_bytes,
            update_ast,
            cdg,
            entry_points,
            break_statements=break_statements,
            continue_statements=continue_statements)
        body += update
        __route_control_flow(local_continue_statements, update[0], cdg)
    else:
        entry_points += local_continue_statements
    __route_control_flow(entry_points, condition[0], cdg)
    for child in body:
        cdg.add_edge(statement, child)
    local_break_statements.append(statement)
    return siblings, local_break_statements


def __handle_for_each(
        statement: Statement,
        source_code_bytes,
        ast: Node,
        cdg: ControlDependenceGraph,
        break_statements: List[Statement] = None,
        continue_statements: List[Statement] = None) -> Tuple[List[Statement], List[Statement]]:
    modifiers_ast = ast.children[0].next_named_sibling
    modifiers_ast = modifiers_ast if modifiers_ast.type == "modifiers" else None
    type_ast = ast.child_by_field_name("type")
    name_ast = ast.child_by_field_name("name")
    if modifiers_ast is None:
        start_point, _ = __parse_position_range(type_ast)
    else:
        start_point, _ = __parse_position_range(modifiers_ast)
    _, end_point = __parse_position_range(name_ast)
    variable = Statement(
        "enhanced_for_variable_declarator",
        STATEMENT_TYPE_VARIABLE,
        start_point=start_point,
        end_point=end_point,
        name=__parse_statement_name(source_code_bytes, name_ast))
    cdg.add_node(variable)
    siblings = [variable]
    entry_points = [variable]
    if modifiers_ast is not None:
        siblings += __parse(
            source_code_bytes,
            modifiers_ast,
            cdg,
            entry_points,
            break_statements=break_statements,
            continue_statements=continue_statements)
    siblings += __parse(
        source_code_bytes,
        type_ast,
        cdg,
        entry_points,
        break_statements=break_statements,
        continue_statements=continue_statements)
    siblings += __parse(
        source_code_bytes,
        name_ast,
        cdg,
        entry_points,
        break_statements=break_statements,
        continue_statements=continue_statements)
    siblings += __parse(
        source_code_bytes,
        ast.child_by_field_name("value"),
        cdg,
        entry_points,
        break_statements=break_statements,
        continue_statements=continue_statements)
    siblings.append(statement)
    __route_control_flow(entry_points, statement, cdg)
    entry_points = [statement]
    local_break_statements = []
    local_continue_statements = []
    body = __parse(
        source_code_bytes,
        ast.child_by_field_name("body"),
        cdg,
        entry_points,
        break_statements=local_break_statements,
        continue_statements=local_continue_statements)
    entry_points += local_continue_statements
    __route_control_flow(entry_points, siblings[0], cdg)
    for child in body:
        cdg.add_edge(statement, child)
    local_break_statements.append(statement)
    return siblings, local_break_statements


def __handle_assignment(
        statement: Statement,
        source_code_bytes,
        ast: Node,
        cdg: ControlDependenceGraph,
        break_statements: List[Statement] = None,
        continue_statements: List[Statement] = None) -> Tuple[List[Statement], List[Statement]]:
    return __handle_statement(statement, source_code_bytes, ast, cdg, break_statements, continue_statements)


def __handle_continue(
        statement: Statement,
        source_code_bytes,
        ast: Node,
        cdg: ControlDependenceGraph,
        break_statements: List[Statement] = None,
        continue_statements: List[Statement] = None) -> Tuple[List[Statement], List[Statement]]:
    continue_statements.append(statement)
    return [statement], []


def __handle_break(
        statement: Statement,
        source_code_bytes,
        ast: Node,
        cdg: ControlDependenceGraph,
        break_statements: List[Statement] = None,
        continue_statements: List[Statement] = None) -> Tuple[List[Statement], List[Statement]]:
    break_statements.append(statement)
    return [statement], []


def __handle_return(
        statement: Statement,
        source_code_bytes,
        ast: Node,
        cdg: ControlDependenceGraph,
        break_statements: List[Statement] = None,
        continue_statements: List[Statement] = None) -> Tuple[List[Statement], List[Statement]]:
    if len(ast.children) > 2:
        entry_points = []
        siblings = __parse(
            source_code_bytes,
            ast.children[1],
            cdg,
            entry_points,
            break_statements=break_statements,
            continue_statements=continue_statements)
        siblings.append(statement)
        __route_control_flow(entry_points, statement, cdg)
    else:
        siblings = [statement]
    return siblings, []


statement_type_and_handler_map = {
    "variable_declarator":
        (STATEMENT_TYPE_VARIABLE, __handle_statement),
    "method_declaration":
        (STATEMENT_TYPE_FUNCTION, __handle_method_declaration),
    "if_statement":
        (STATEMENT_TYPE_BRANCH, __handle_if),
    "try_statement":
        (STATEMENT_TYPE_BRANCH, __handle_try),
    "try_with_resources_statement":
        (STATEMENT_TYPE_BRANCH, __handle_try),
    "catch_clause":
        (STATEMENT_TYPE_BRANCH, __handle_catch),
    "catch_formal_parameter":
        (STATEMENT_TYPE_VARIABLE, __handle_statement),
    "while_statement":
        (STATEMENT_TYPE_LOOP, __handle_for),
    "for_statement":
        (STATEMENT_TYPE_LOOP, __handle_for),
    "enhanced_for_statement":
        (STATEMENT_TYPE_LOOP, __handle_for_each),
    "assignment_expression":
        (STATEMENT_TYPE_ASSIGNMENT, __handle_assignment),
    "method_invocation":
        (STATEMENT_TYPE_CALL, __handle_statement),
    "block":
        (STATEMENT_TYPE_STATEMENTS, __handle_statement),
    "continue_statement":
        (STATEMENT_TYPE_GOTO, __handle_continue),
    "break_statement":
        (STATEMENT_TYPE_GOTO, __handle_break),
    "return_statement":
        (STATEMENT_TYPE_EXIT, __handle_return)
}


def parse(source_code: str) -> ControlDependenceGraph:
    """
    Parse the source code string into a Control Dependence Graph.
    :param source_code: the string that should to be parsed.
    :return: Control Dependence Graph
    """
    source_code_bytes = bytes(source_code, "utf8")
    ast = parser.parse(source_code_bytes)
    result = ControlDependenceGraph()
    __parse(source_code_bytes, ast.root_node, result, [])
    return result


def __parse(
        source_code_bytes: bytes,
        ast: Node,
        cdg: ControlDependenceGraph,
        entry_points: List[Statement],
        break_statements: List[Statement] = None,
        continue_statements: List[Statement] = None) -> List[Statement]:
    """
    Parse the tree_sitter ast into a Control Dependence Graph.
    :param ast: tree_sitter Node.
    :param cdg: Control Dependence Graph that will contain parsed Statements.
    :return: Statements that are siblings and should be placed instead of the given ast Node.
    """
    statement_type, statement_handler = __parse_statement_type_and_handler(ast)
    start_point, end_point = __parse_position_range(ast)
    statement = Statement(
        ast.type,
        statement_type,
        start_point=start_point,
        end_point=end_point,
        name=__parse_statement_name(source_code_bytes, ast))
    cdg.add_node(statement)

    siblings, exit_points = statement_handler(
        statement,
        source_code_bytes,
        ast,
        cdg,
        break_statements=break_statements,
        continue_statements=continue_statements)
    if siblings:
        __route_control_flow(entry_points, siblings[0], cdg)
    entry_points.clear()
    for exit_point in exit_points:
        entry_points.append(exit_point)
    return siblings


def __parse_statement_type_and_handler(ast: Node) -> Tuple[str, Callable]:
    return statement_type_and_handler_map.get(ast.type, (STATEMENT_TYPE_OBJECT, __handle_statement))


def __parse_position_range(ast: Node) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    return ast.start_point, ast.end_point


def __parse_statement_name(source_code_bytes: bytes, ast: Node) -> Optional[str]:
    if ast.type == "variable_declarator":
        return __parse_statement_name(source_code_bytes, ast.child_by_field_name("name"))
    elif ast.type == "assignment_expression":
        return __parse_statement_name(source_code_bytes, ast.child_by_field_name("left"))
    elif ast.type == "catch_formal_parameter":
        return __parse_statement_name(source_code_bytes, ast.child_by_field_name("name"))
    elif ast.start_point[0] == ast.end_point[0]:
        return source_code_bytes[ast.start_byte: ast.end_byte].decode("utf8")
    return None


def __route_control_flow(
        statements_from: List[Statement],
        statement_to: Statement,
        cdg: ControlDependenceGraph) -> None:
    for entry_point in statements_from:
        if entry_point not in cdg.control_flow:
            cdg.control_flow[entry_point] = [statement_to]
        else:
            cdg.control_flow[entry_point].append(statement_to)

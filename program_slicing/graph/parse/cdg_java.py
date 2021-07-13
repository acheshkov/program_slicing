__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/30'

from typing import List, Tuple, Set, Callable

from tree_sitter import Node

from program_slicing.graph.parse import tree_sitter_ast_java
from program_slicing.graph.parse import tree_sitter_parsers
from program_slicing.graph.cdg import ControlDependenceGraph
from program_slicing.graph.statement import Statement, StatementType
from program_slicing.graph.point import Point


def __handle_statement(
        statement: Statement,
        source_code_bytes,
        ast: Node,
        cdg: ControlDependenceGraph,
        break_statements: List[Statement],
        continue_statements: List[Statement],
        exit_statements: List[Statement],
        variable_names: Set[str]) -> Tuple[List[Statement], List[Statement]]:
    siblings = [statement]
    entry_points = [statement]
    name = ast.child_by_field_name("name")
    for child in ast.children:
        if not child.is_named or child == name:
            continue
        siblings += __parse(
            source_code_bytes,
            child,
            cdg,
            entry_points,
            break_statements=break_statements,
            continue_statements=continue_statements,
            exit_statements=exit_statements,
            variable_names=variable_names)
    return siblings, entry_points


def __handle_variable(
        statement: Statement,
        source_code_bytes,
        ast: Node,
        cdg: ControlDependenceGraph,
        break_statements: List[Statement],
        continue_statements: List[Statement],
        exit_statements: List[Statement],
        variable_names: Set[str]) -> Tuple[List[Statement], List[Statement]]:
    variable_names.add(tree_sitter_parsers.node_name(source_code_bytes, ast))
    return __handle_statement(
        statement,
        source_code_bytes,
        ast,
        cdg,
        break_statements=break_statements,
        continue_statements=continue_statements,
        exit_statements=exit_statements,
        variable_names=variable_names)


def __handle_method_declaration(
        statement: Statement,
        source_code_bytes,
        ast: Node,
        cdg: ControlDependenceGraph,
        break_statements: List[Statement],
        continue_statements: List[Statement],
        exit_statements: List[Statement],
        variable_names: Set[str]) -> Tuple[List[Statement], List[Statement]]:
    cdg.add_entry_point(statement)
    entry_points = [statement]
    local_exit_statements = []
    children = __parse(
        source_code_bytes,
        ast.child_by_field_name("body"),
        cdg,
        entry_points,
        break_statements=break_statements,
        continue_statements=continue_statements,
        exit_statements=local_exit_statements,
        variable_names=variable_names)
    children.append(__add_exit_point(cdg, statement, entry_points + local_exit_statements))
    for child in children:
        cdg.add_edge(statement, child)
    return [], []


def __handle_switch(
        statement: Statement,
        source_code_bytes,
        ast: Node,
        cdg: ControlDependenceGraph,
        break_statements: List[Statement],
        continue_statements: List[Statement],
        exit_statements: List[Statement],
        variable_names: Set[str]) -> Tuple[List[Statement], List[Statement]]:
    entry_points = []
    siblings = __parse(
        source_code_bytes,
        ast.child_by_field_name("condition"),
        cdg,
        entry_points,
        break_statements=break_statements,
        continue_statements=continue_statements,
        exit_statements=exit_statements,
        variable_names=variable_names)
    switch_block_ast = ast.child_by_field_name("body")
    switch_block_start_point, switch_block_end_point = __parse_position_range(switch_block_ast)
    block_statement = Statement(
        StatementType.SCOPE,
        start_point=switch_block_start_point,
        end_point=switch_block_end_point,
        affected_by=__parse_affected_by(source_code_bytes, switch_block_ast, variable_names),
        ast_node_type=switch_block_ast.type)
    siblings.append(block_statement)
    __route_control_flow(entry_points, block_statement, cdg)
    entry_points = [block_statement]
    siblings.append(statement)
    __route_control_flow(entry_points, statement, cdg)
    switch_block_item_ast = switch_block_ast.children[0].next_named_sibling if switch_block_ast.children else None
    local_break_statements = []
    entry_points = []
    while switch_block_item_ast is not None:
        if switch_block_item_ast.type == "switch_label":
            switch_label_start_point = Point.from_tuple(switch_block_item_ast.start_point)
            switch_label_statement = Statement(
                StatementType.SCOPE,
                start_point=switch_label_start_point,
                end_point=switch_block_end_point,
                ast_node_type=switch_block_item_ast.type)
            cdg.add_edge(statement, switch_label_statement)
            __route_control_flow([statement], switch_label_statement, cdg)
            __route_control_flow(entry_points, switch_label_statement, cdg)
            entry_points = [switch_label_statement]
            switch_block_item_ast = switch_block_item_ast.next_named_sibling
            continue
        switch_block_item = __parse(
            source_code_bytes,
            switch_block_item_ast,
            cdg,
            entry_points,
            break_statements=local_break_statements,
            continue_statements=continue_statements,
            exit_statements=exit_statements,
            variable_names=variable_names)
        for child in switch_block_item:
            cdg.add_edge(statement, child)
        switch_block_item_ast = switch_block_item_ast.next_named_sibling
    return siblings, [statement] + entry_points + local_break_statements


def __handle_if(
        statement: Statement,
        source_code_bytes,
        ast: Node,
        cdg: ControlDependenceGraph,
        break_statements: List[Statement],
        continue_statements: List[Statement],
        exit_statements: List[Statement],
        variable_names: Set[str]) -> Tuple[List[Statement], List[Statement]]:
    entry_points = []
    siblings = __parse(
        source_code_bytes,
        ast.child_by_field_name("condition"),
        cdg,
        entry_points,
        break_statements=break_statements,
        continue_statements=continue_statements,
        exit_statements=exit_statements,
        variable_names=variable_names)
    siblings.append(statement)
    __route_control_flow(entry_points, statement, cdg)
    entry_points = [statement]
    consequence = __parse(
        source_code_bytes,
        ast.child_by_field_name("consequence"),
        cdg,
        entry_points,
        break_statements=break_statements,
        continue_statements=continue_statements,
        exit_statements=exit_statements,
        variable_names=variable_names)
    for child in consequence:
        cdg.add_edge(statement, child)
    alternative_ast = ast.child_by_field_name("alternative")
    alternative_entry_points = [statement]
    if alternative_ast is not None:
        else_ast = alternative_ast.prev_sibling
        start_point, end_point = __parse_position_range(else_ast)
        else_statement = Statement(
            StatementType.GOTO,
            start_point=start_point,
            end_point=end_point,
            affected_by=set(),
            ast_node_type=else_ast.type)
        cdg.add_edge(statement, else_statement)
        __route_control_flow(alternative_entry_points, else_statement, cdg)
        alternative_entry_points = [else_statement]
        alternative = __parse(
            source_code_bytes,
            alternative_ast,
            cdg,
            alternative_entry_points,
            break_statements=break_statements,
            continue_statements=continue_statements,
            exit_statements=exit_statements,
            variable_names=variable_names)
        for child in alternative:
            cdg.add_edge(statement, child)
    return siblings, entry_points + alternative_entry_points


def __handle_try(
        statement: Statement,
        source_code_bytes,
        ast: Node,
        cdg: ControlDependenceGraph,
        break_statements: List[Statement],
        continue_statements: List[Statement],
        exit_statements: List[Statement],
        variable_names: Set[str]) -> Tuple[List[Statement], List[Statement]]:
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
            continue_statements=continue_statements,
            exit_statements=exit_statements,
            variable_names=variable_names)
    siblings.append(statement)
    __route_control_flow(entry_points, statement, cdg)
    entry_points = [statement]
    body_ast = ast.child_by_field_name("body")
    body = __parse(
        source_code_bytes,
        body_ast,
        cdg,
        entry_points,
        break_statements=break_statements,
        continue_statements=continue_statements,
        exit_statements=exit_statements,
        variable_names=variable_names)
    for child in body:
        cdg.add_edge(statement, child)
    exit_points = [] + entry_points
    entry_points = [statement]
    clause_ast = body_ast.next_named_sibling
    while clause_ast is not None and clause_ast.type != "finally_clause":
        clause = __parse(
            source_code_bytes,
            clause_ast,
            cdg,
            entry_points,
            break_statements=break_statements,
            continue_statements=continue_statements,
            exit_statements=exit_statements,
            variable_names=variable_names,
            end_point=statement.end_point)
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
            continue_statements=continue_statements,
            exit_statements=exit_statements,
            variable_names=variable_names,
            end_point=statement.end_point)
    return siblings, exit_points


def __handle_catch(
        statement: Statement,
        source_code_bytes,
        ast: Node,
        cdg: ControlDependenceGraph,
        break_statements: List[Statement],
        continue_statements: List[Statement],
        exit_statements: List[Statement],
        variable_names: Set[str]) -> Tuple[List[Statement], List[Statement]]:
    entry_points = []
    siblings = __parse(
        source_code_bytes,
        ast.child_by_field_name("body").prev_named_sibling,
        cdg,
        entry_points,
        break_statements=break_statements,
        continue_statements=continue_statements,
        exit_statements=exit_statements,
        variable_names=variable_names)
    siblings.append(statement)
    __route_control_flow(entry_points, statement, cdg)
    entry_points = [statement]
    body = __parse(
        source_code_bytes,
        ast.child_by_field_name("body"),
        cdg,
        entry_points,
        break_statements=break_statements,
        continue_statements=continue_statements,
        exit_statements=exit_statements,
        variable_names=variable_names)
    for child in body:
        cdg.add_edge(statement, child)
    return siblings, entry_points


def __handle_for(
        statement: Statement,
        source_code_bytes,
        ast: Node,
        cdg: ControlDependenceGraph,
        break_statements: List[Statement],
        continue_statements: List[Statement],
        exit_statements: List[Statement],
        variable_names: Set[str]) -> Tuple[List[Statement], List[Statement]]:
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
            continue_statements=continue_statements,
            exit_statements=exit_statements,
            variable_names=variable_names)
    condition_ast = ast.child_by_field_name("condition")
    condition = []
    if condition_ast is not None:
        condition = __parse(
            source_code_bytes,
            condition_ast,
            cdg,
            entry_points,
            break_statements=break_statements,
            continue_statements=continue_statements,
            exit_statements=exit_statements,
            variable_names=variable_names)
    condition.append(statement)
    siblings += condition
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
        continue_statements=local_continue_statements,
        exit_statements=exit_statements,
        variable_names=variable_names)
    update_ast = ast.child_by_field_name("update")
    if update_ast is not None:
        update = __parse(
            source_code_bytes,
            update_ast,
            cdg,
            entry_points,
            break_statements=break_statements,
            continue_statements=continue_statements,
            exit_statements=exit_statements,
            variable_names=variable_names)
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
        break_statements: List[Statement],
        continue_statements: List[Statement],
        exit_statements: List[Statement],
        variable_names: Set[str]) -> Tuple[List[Statement], List[Statement]]:
    modifiers_ast = ast.children[0].next_named_sibling
    modifiers_ast = modifiers_ast if modifiers_ast.type == "modifiers" else None
    type_ast = ast.child_by_field_name("type")
    name_ast = ast.child_by_field_name("name")
    value_ast = ast.child_by_field_name("value")
    if modifiers_ast is None:
        start_point, _ = __parse_position_range(type_ast)
    else:
        start_point, _ = __parse_position_range(modifiers_ast)
    _, end_point = __parse_position_range(name_ast)
    variable = Statement(
        StatementType.VARIABLE,
        start_point=start_point,
        end_point=end_point,
        affected_by=__parse_affected_by(source_code_bytes, value_ast, variable_names),
        name=tree_sitter_parsers.node_name(source_code_bytes, name_ast),
        ast_node_type="enhanced_for_variable_declarator")
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
            continue_statements=continue_statements,
            exit_statements=exit_statements,
            variable_names=variable_names)
    siblings += __parse(
        source_code_bytes,
        type_ast,
        cdg,
        entry_points,
        break_statements=break_statements,
        continue_statements=continue_statements,
        exit_statements=exit_statements,
        variable_names=variable_names)
    siblings += __parse(
        source_code_bytes,
        name_ast,
        cdg,
        entry_points,
        break_statements=break_statements,
        continue_statements=continue_statements,
        exit_statements=exit_statements,
        variable_names=variable_names)
    siblings += __parse(
        source_code_bytes,
        value_ast,
        cdg,
        entry_points,
        break_statements=break_statements,
        continue_statements=continue_statements,
        exit_statements=exit_statements,
        variable_names=variable_names)
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
        continue_statements=local_continue_statements,
        exit_statements=exit_statements,
        variable_names=variable_names)
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
        break_statements: List[Statement],
        continue_statements: List[Statement],
        exit_statements: List[Statement],
        variable_names: Set[str]) -> Tuple[List[Statement], List[Statement]]:
    entry_points = []
    siblings = __parse(
        source_code_bytes,
        ast.child_by_field_name("left"),
        cdg,
        entry_points,
        break_statements=break_statements,
        continue_statements=continue_statements,
        exit_statements=exit_statements,
        variable_names=variable_names)
    siblings += __parse(
        source_code_bytes,
        ast.child_by_field_name("right"),
        cdg,
        entry_points,
        break_statements=break_statements,
        continue_statements=continue_statements,
        exit_statements=exit_statements,
        variable_names=variable_names)
    siblings.append(statement)
    __route_control_flow(entry_points, statement, cdg)
    entry_points = [statement]
    return siblings, entry_points


def __handle_update(
        statement: Statement,
        source_code_bytes,
        ast: Node,
        cdg: ControlDependenceGraph,
        break_statements: List[Statement],
        continue_statements: List[Statement],
        exit_statements: List[Statement],
        variable_names: Set[str]) -> Tuple[List[Statement], List[Statement]]:
    entry_points = []
    expression_ast = ast.children[0]
    expression_ast = expression_ast if expression_ast.next_named_sibling is None else expression_ast.next_named_sibling
    siblings = __parse(
        source_code_bytes,
        expression_ast,
        cdg,
        entry_points,
        break_statements=break_statements,
        continue_statements=continue_statements,
        exit_statements=exit_statements,
        variable_names=variable_names)
    siblings.append(statement)
    __route_control_flow(entry_points, statement, cdg)
    entry_points = [statement]
    return siblings, entry_points


def __handle_continue(
        statement: Statement,
        source_code_bytes,
        ast: Node,
        cdg: ControlDependenceGraph,
        break_statements: List[Statement],
        continue_statements: List[Statement],
        exit_statements: List[Statement],
        variable_names: Set[str]) -> Tuple[List[Statement], List[Statement]]:
    continue_statements.append(statement)
    return [statement], []


def __handle_break(
        statement: Statement,
        source_code_bytes,
        ast: Node,
        cdg: ControlDependenceGraph,
        break_statements: List[Statement],
        continue_statements: List[Statement],
        exit_statements: List[Statement],
        variable_names=Set[str]) -> Tuple[List[Statement], List[Statement]]:
    break_statements.append(statement)
    return [statement], []


def __handle_return(
        statement: Statement,
        source_code_bytes,
        ast: Node,
        cdg: ControlDependenceGraph,
        break_statements: List[Statement],
        continue_statements: List[Statement],
        exit_statements: List[Statement],
        variable_names: Set[str]) -> Tuple[List[Statement], List[Statement]]:
    if len(ast.children) > 2:
        entry_points = []
        siblings = __parse(
            source_code_bytes,
            ast.children[1],
            cdg,
            entry_points,
            break_statements=break_statements,
            continue_statements=continue_statements,
            exit_statements=exit_statements,
            variable_names=variable_names)
        siblings.append(statement)
        __route_control_flow(entry_points, statement, cdg)
    else:
        siblings = [statement]
    exit_statements.append(statement)
    return siblings, []


statement_type_and_handler_map = {
    "variable_declarator":
        (StatementType.VARIABLE, __handle_variable),
    "method_declaration":
        (StatementType.FUNCTION, __handle_method_declaration),
    "constructor_declaration":
        (StatementType.FUNCTION, __handle_method_declaration),
    "switch_statement":
        (StatementType.BRANCH, __handle_switch),
    "if_statement":
        (StatementType.BRANCH, __handle_if),
    "try_statement":
        (StatementType.BRANCH, __handle_try),
    "try_with_resources_statement":
        (StatementType.BRANCH, __handle_try),
    "catch_clause":
        (StatementType.BRANCH, __handle_catch),
    "catch_formal_parameter":
        (StatementType.VARIABLE, __handle_variable),
    "while_statement":
        (StatementType.LOOP, __handle_for),
    "for_statement":
        (StatementType.LOOP, __handle_for),
    "enhanced_for_statement":
        (StatementType.LOOP, __handle_for_each),
    "assignment_expression":
        (StatementType.ASSIGNMENT, __handle_assignment),
    "update_expression":
        (StatementType.ASSIGNMENT, __handle_update),
    "method_invocation":
        (StatementType.CALL, __handle_statement),
    "block":
        (StatementType.SCOPE, __handle_statement),
    "constructor_body":
        (StatementType.SCOPE, __handle_statement),
    "continue_statement":
        (StatementType.GOTO, __handle_continue),
    "break_statement":
        (StatementType.GOTO, __handle_break),
    "return_statement":
        (StatementType.GOTO, __handle_return),
    "throw_statement":
        (StatementType.GOTO, __handle_return)
}


def parse(source_code: str) -> ControlDependenceGraph:
    """
    Parse the source code string into a Control Dependence Graph.
    :param source_code: the string that should to be parsed.
    :return: Control Dependence Graph.
    """
    source_code_bytes = bytes(source_code, "utf8")
    ast = tree_sitter_ast_java.parse(source_code).root_node
    result = ControlDependenceGraph()
    if __parse_undeclared_class(source_code_bytes, ast, result):
        result.build_scope_dependency()
        return result
    if __parse_undeclared_method(source_code_bytes, ast, result):
        result.build_scope_dependency()
        return result
    __parse(source_code_bytes, ast, result, [], [], [], [], set())
    result.build_scope_dependency()
    return result


def __parse(
        source_code_bytes: bytes,
        ast: Node,
        cdg: ControlDependenceGraph,
        entry_points: List[Statement],
        break_statements: List[Statement],
        continue_statements: List[Statement],
        exit_statements: List[Statement],
        variable_names: Set[str],
        start_point: Point = None,
        end_point: Point = None) -> List[Statement]:
    """
    Parse the tree_sitter ast into a Control Dependence Graph.
    :param ast: tree_sitter Node.
    :param cdg: Control Dependence Graph that will contain parsed Statements.
    :return: Statements that are siblings and should be placed instead of the given ast Node.
    """
    statement_type, statement_handler = __parse_statement_type_and_handler(ast)
    __start_point, __end_point = __parse_position_range(ast)
    if start_point is None:
        start_point = __start_point
    if end_point is None:
        end_point = __end_point
    statement = Statement(
        statement_type,
        start_point=start_point,
        end_point=end_point,
        affected_by=__parse_affected_by(source_code_bytes, ast, variable_names),
        name=tree_sitter_parsers.node_name(source_code_bytes, ast),
        ast_node_type=ast.type)
    cdg.add_node(statement)
    siblings, exit_points = statement_handler(
        statement,
        source_code_bytes,
        ast,
        cdg,
        break_statements=break_statements,
        continue_statements=continue_statements,
        exit_statements=exit_statements,
        variable_names=variable_names)
    if siblings:
        __route_control_flow(entry_points, siblings[0], cdg)
        entry_points.clear()
        for exit_point in exit_points:
            entry_points.append(exit_point)
    return siblings


def __parse_undeclared_class(source_code_bytes: bytes, ast: Node, cdg: ControlDependenceGraph) -> bool:
    result = False
    for node in ast.children:
        if node.type == "ERROR" and \
                node.next_named_sibling is not None and \
                node.prev_named_sibling is not None and \
                node.next_named_sibling.type == "block" and \
                node.prev_named_sibling.type == "local_variable_declaration":
            result = True
            scope = node.next_named_sibling
            declaration = node.prev_named_sibling
            start_point, end_point = __parse_position_range(scope)
            entry_point = Statement(
                StatementType.FUNCTION,
                start_point=start_point,
                end_point=end_point,
                affected_by=set(),
                name=tree_sitter_parsers.node_name(source_code_bytes, declaration.children[-1]),
                ast_node_type="method_declaration")
            cdg.add_node(entry_point)
            cdg.add_entry_point(entry_point)
            entry_points = [entry_point]
            exit_statements = []
            for child in __parse(source_code_bytes, scope, cdg, entry_points, [], [], exit_statements, set()):
                cdg.add_edge(entry_point, child)
            exit_point = __add_exit_point(cdg, entry_point, entry_points + exit_statements)
            cdg.add_edge(entry_point, exit_point)
    return result


def __parse_undeclared_method(source_code_bytes: bytes, ast: Node, cdg: ControlDependenceGraph) -> bool:
    if not {
        "class_declaration",
        "enum_declaration",
        "interface_declaration",
    }.intersection({node.type for node in ast.children}):
        start_point, end_point = __parse_position_range(ast)
        entry_point = Statement(
            StatementType.FUNCTION,
            start_point=start_point,
            end_point=end_point,
            affected_by=set(),
            name="",
            ast_node_type="method_declaration")
        cdg.add_node(entry_point)
        cdg.add_entry_point(entry_point)
        entry_points = [entry_point]
        break_statements = []
        continue_statements = []
        exit_statements = []
        variable_names = set()
        for node in ast.children:
            for child in __parse(
                    source_code_bytes,
                    node,
                    cdg,
                    entry_points,
                    break_statements=break_statements,
                    continue_statements=continue_statements,
                    exit_statements=exit_statements,
                    variable_names=variable_names):
                cdg.add_edge(entry_point, child)
        exit_point = __add_exit_point(cdg, entry_point, entry_points + exit_statements)
        cdg.add_edge(entry_point, exit_point)
        return True
    else:
        return False


def __parse_statement_type_and_handler(ast: Node) -> Tuple[StatementType, Callable]:
    return statement_type_and_handler_map.get(ast.type, (StatementType.UNKNOWN, __handle_statement))


def __parse_position_range(ast: Node) -> Tuple[Point, Point]:
    return Point.from_tuple(ast.start_point), Point.from_tuple(ast.end_point)


def __parse_affected_by(source_code_bytes: bytes, ast: Node, variable_names: Set[str]) -> Set[str]:
    #  TODO: this approach is ineffective, we can use list of sibling Statements with previously counted results.
    affected_by: Set[str] = set()
    __parse_affected_by_recursive(source_code_bytes, ast, variable_names, affected_by)
    return affected_by


def __parse_affected_by_recursive(
        source_code_bytes: bytes,
        ast: Node,
        variable_names: Set[str],
        affected_by: Set[str]) -> None:
    body = ast.child_by_field_name("body")
    consequence = ast.child_by_field_name("consequence")
    alternative = ast.child_by_field_name("alternative")
    name = tree_sitter_parsers.node_name(source_code_bytes, ast)
    if name in variable_names:
        affected_by.add(name)
    for child in ast.children:
        if child.type == "block" or child == body or child == consequence or child == alternative:
            continue
        __parse_affected_by_recursive(source_code_bytes, child, variable_names, affected_by)


def __add_exit_point(cdg: ControlDependenceGraph, statement: Statement, entry_points: List[Statement]) -> Statement:
    affected_by = set()
    for exit_point in entry_points:
        if exit_point.statement_type == StatementType.GOTO:
            affected_by.update(exit_point.affected_by)
    exit_point = Statement(
        StatementType.EXIT,
        start_point=statement.end_point,
        end_point=statement.end_point,
        affected_by=affected_by,
        name=None,
        ast_node_type="exit_point")
    cdg.add_node(exit_point)
    __route_control_flow(entry_points, exit_point, cdg)
    return exit_point


def __route_control_flow(
        statements_from: List[Statement],
        statement_to: Statement,
        cdg: ControlDependenceGraph) -> None:
    for entry_point in statements_from:
        if entry_point not in cdg.control_flow:
            cdg.control_flow[entry_point] = [statement_to]
        else:
            cdg.control_flow[entry_point].append(statement_to)

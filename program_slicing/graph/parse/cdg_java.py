__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/30'

from typing import List, Tuple, Callable, Optional

from tree_sitter import Node

from program_slicing.graph.parse import tree_sitter_parsers
from program_slicing.graph.cdg import ControlDependenceGraph
from program_slicing.graph.cdg_node import CDGNode, \
    CDG_NODE_TYPE_FUNCTION, \
    CDG_NODE_TYPE_VARIABLE, \
    CDG_NODE_TYPE_ASSIGNMENT, \
    CDG_NODE_TYPE_CALL, \
    CDG_NODE_TYPE_STATEMENTS, \
    CDG_NODE_TYPE_BRANCH, \
    CDG_NODE_TYPE_LOOP, \
    CDG_NODE_TYPE_GOTO, \
    CDG_NODE_TYPE_OBJECT, \
    CDG_NODE_TYPE_EXIT


parser = tree_sitter_parsers.java()


def __handle_node(
        node: CDGNode,
        source_code_bytes,
        ast: Node,
        cdg: ControlDependenceGraph,
        break_nodes: List[CDGNode] = None,
        continue_nodes: List[CDGNode] = None) -> Tuple[List[CDGNode], List[CDGNode]]:
    siblings = [node]
    entry_points = [node]
    for child in ast.children:
        siblings += __parse(
            source_code_bytes,
            child,
            cdg,
            entry_points,
            break_nodes=break_nodes,
            continue_nodes=continue_nodes)
    return siblings, entry_points


def __handle_method_declaration(
        node: CDGNode,
        source_code_bytes,
        ast: Node,
        cdg: ControlDependenceGraph,
        break_nodes: List[CDGNode] = None,
        continue_nodes: List[CDGNode] = None) -> Tuple[List[CDGNode], List[CDGNode]]:
    cdg.add_entry_point(node)
    siblings = [node]
    entry_points = [node]
    children = __parse(
        source_code_bytes,
        ast.child_by_field_name("body"),
        cdg,
        entry_points,
        break_nodes=break_nodes,
        continue_nodes=continue_nodes)
    for child in children:
        cdg.add_edge(node, child)
    return siblings, entry_points


def __handle_if(
        node: CDGNode,
        source_code_bytes,
        ast: Node,
        cdg: ControlDependenceGraph,
        break_nodes: List[CDGNode] = None,
        continue_nodes: List[CDGNode] = None) -> Tuple[List[CDGNode], List[CDGNode]]:
    entry_points = []
    siblings = __parse(
        source_code_bytes,
        ast.child_by_field_name("condition"),
        cdg,
        entry_points,
        break_nodes=break_nodes,
        continue_nodes=continue_nodes)
    siblings.append(node)
    __route_control_flow(entry_points, node, cdg)
    entry_points = [node]
    consequence = __parse(
        source_code_bytes,
        ast.child_by_field_name("consequence"),
        cdg,
        entry_points,
        break_nodes=break_nodes,
        continue_nodes=continue_nodes)
    for child in consequence:
        cdg.add_edge(node, child)
    alternative_ast = ast.child_by_field_name("alternative")
    alternative_entry_points = [node]
    if alternative_ast is not None:
        alternative = __parse(
            source_code_bytes,
            alternative_ast,
            cdg,
            alternative_entry_points,
            break_nodes=break_nodes,
            continue_nodes=continue_nodes)
        for child in alternative:
            cdg.add_edge(node, child)

    return siblings, entry_points + alternative_entry_points


def __handle_try(
        node: CDGNode,
        source_code_bytes,
        ast: Node,
        cdg: ControlDependenceGraph,
        break_nodes: List[CDGNode] = None,
        continue_nodes: List[CDGNode] = None) -> Tuple[List[CDGNode], List[CDGNode]]:
    siblings = []
    entry_points = []
    resources_ast = ast.child_by_field_name("resources")
    if resources_ast is not None:
        siblings += __parse(
            source_code_bytes,
            resources_ast,
            cdg,
            entry_points,
            break_nodes=break_nodes,
            continue_nodes=continue_nodes)
    body_ast = ast.child_by_field_name("body")
    siblings += __parse(
        source_code_bytes,
        body_ast,
        cdg,
        entry_points,
        break_nodes=break_nodes,
        continue_nodes=continue_nodes)
    siblings.append(node)
    __route_control_flow(entry_points, node, cdg)
    exit_nodes = [node]
    entry_points = [node]
    clause_ast = body_ast.next_named_sibling
    while clause_ast is not None and clause_ast.type != "finally_clause":
        clause = __parse(
            source_code_bytes,
            clause_ast,
            cdg,
            entry_points,
            break_nodes=break_nodes,
            continue_nodes=continue_nodes)
        for child in clause:
            cdg.add_edge(node, child)
        node = clause[-1]
        exit_nodes += entry_points
        entry_points = [node]
        clause_ast = clause_ast.next_named_sibling
    if exit_nodes != entry_points:
        exit_nodes += entry_points
    if clause_ast is not None:
        siblings += __parse(
            source_code_bytes,
            clause_ast,
            cdg,
            exit_nodes,
            break_nodes=break_nodes,
            continue_nodes=continue_nodes)
    return siblings, exit_nodes


def __handle_catch(
        node: CDGNode,
        source_code_bytes,
        ast: Node,
        cdg: ControlDependenceGraph,
        break_nodes: List[CDGNode] = None,
        continue_nodes: List[CDGNode] = None) -> Tuple[List[CDGNode], List[CDGNode]]:
    entry_points = []
    siblings = __parse(
        source_code_bytes,
        ast.child_by_field_name("body").prev_named_sibling,
        cdg,
        entry_points,
        break_nodes=break_nodes,
        continue_nodes=continue_nodes)
    siblings.append(node)
    __route_control_flow(entry_points, node, cdg)
    entry_points = [node]
    body = __parse(
        source_code_bytes,
        ast.child_by_field_name("body"),
        cdg,
        entry_points,
        break_nodes=break_nodes,
        continue_nodes=continue_nodes)
    for child in body:
        cdg.add_edge(node, child)
    return siblings, entry_points


def __handle_for(
        node: CDGNode,
        source_code_bytes,
        ast: Node,
        cdg: ControlDependenceGraph,
        break_nodes: List[CDGNode] = None,
        continue_nodes: List[CDGNode] = None) -> Tuple[List[CDGNode], List[CDGNode]]:
    siblings = []
    entry_points = []
    init_ast = ast.child_by_field_name("init")
    if init_ast is not None:
        siblings += __parse(
            source_code_bytes,
            init_ast,
            cdg,
            entry_points,
            break_nodes=break_nodes,
            continue_nodes=continue_nodes)
    condition = __parse(
        source_code_bytes,
        ast.child_by_field_name("condition"),
        cdg,
        entry_points,
        break_nodes=break_nodes,
        continue_nodes=continue_nodes)
    siblings += condition
    siblings.append(node)
    __route_control_flow(entry_points, node, cdg)
    entry_points = [node]
    local_break_nodes = []
    local_continue_nodes = []
    body = __parse(
        source_code_bytes,
        ast.child_by_field_name("body"),
        cdg,
        entry_points,
        break_nodes=local_break_nodes,
        continue_nodes=local_continue_nodes)
    update_ast = ast.child_by_field_name("update")
    if update_ast is not None:
        update = __parse(
            source_code_bytes,
            update_ast,
            cdg,
            entry_points,
            break_nodes=break_nodes,
            continue_nodes=continue_nodes)
        body += update
        __route_control_flow(local_continue_nodes, update[0], cdg)
    else:
        entry_points += local_continue_nodes
    __route_control_flow(entry_points, condition[0], cdg)
    for child in body:
        cdg.add_edge(node, child)
    local_break_nodes.append(node)
    return siblings, local_break_nodes


def __handle_for_each(
        node: CDGNode,
        source_code_bytes,
        ast: Node,
        cdg: ControlDependenceGraph,
        break_nodes: List[CDGNode] = None,
        continue_nodes: List[CDGNode] = None) -> Tuple[List[CDGNode], List[CDGNode]]:
    modifiers_ast = ast.children[0].next_named_sibling
    modifiers_ast = modifiers_ast if modifiers_ast.type == "modifiers" else None
    type_ast = ast.child_by_field_name("type")
    name_ast = ast.child_by_field_name("name")
    if modifiers_ast is None:
        start_point, _ = __parse_position_range(type_ast)
    else:
        start_point, _ = __parse_position_range(modifiers_ast)
    _, end_point = __parse_position_range(name_ast)
    variable = CDGNode(
        "enhanced_for_variable_declarator",
        CDG_NODE_TYPE_VARIABLE,
        start_point=start_point,
        end_point=end_point,
        name=__parse_node_name(source_code_bytes, name_ast))
    cdg.add_node(variable)
    siblings = [variable]
    entry_points = [variable]
    if modifiers_ast is not None:
        siblings += __parse(
            source_code_bytes,
            modifiers_ast,
            cdg,
            entry_points,
            break_nodes=break_nodes,
            continue_nodes=continue_nodes)
    siblings += __parse(
        source_code_bytes,
        type_ast,
        cdg,
        entry_points,
        break_nodes=break_nodes,
        continue_nodes=continue_nodes)
    siblings += __parse(
        source_code_bytes,
        name_ast,
        cdg,
        entry_points,
        break_nodes=break_nodes,
        continue_nodes=continue_nodes)
    siblings += __parse(
        source_code_bytes,
        ast.child_by_field_name("value"),
        cdg,
        entry_points,
        break_nodes=break_nodes,
        continue_nodes=continue_nodes)
    siblings.append(node)
    __route_control_flow(entry_points, node, cdg)
    entry_points = [node]
    local_break_nodes = []
    local_continue_nodes = []
    body = __parse(
        source_code_bytes,
        ast.child_by_field_name("body"),
        cdg,
        entry_points,
        break_nodes=local_break_nodes,
        continue_nodes=local_continue_nodes)
    entry_points += local_continue_nodes
    __route_control_flow(entry_points, siblings[0], cdg)
    for child in body:
        cdg.add_edge(node, child)
    local_break_nodes.append(node)
    return siblings, local_break_nodes


def __handle_assignment(
        node: CDGNode,
        source_code_bytes,
        ast: Node,
        cdg: ControlDependenceGraph,
        break_nodes: List[CDGNode] = None,
        continue_nodes: List[CDGNode] = None) -> Tuple[List[CDGNode], List[CDGNode]]:
    return __handle_node(node, source_code_bytes, ast, cdg, break_nodes, continue_nodes)


def __handle_continue(
        node: CDGNode,
        source_code_bytes,
        ast: Node,
        cdg: ControlDependenceGraph,
        break_nodes: List[CDGNode] = None,
        continue_nodes: List[CDGNode] = None) -> Tuple[List[CDGNode], List[CDGNode]]:
    continue_nodes.append(node)
    return [node], []


def __handle_break(
        node: CDGNode,
        source_code_bytes,
        ast: Node,
        cdg: ControlDependenceGraph,
        break_nodes: List[CDGNode] = None,
        continue_nodes: List[CDGNode] = None) -> Tuple[List[CDGNode], List[CDGNode]]:
    break_nodes.append(node)
    return [node], []


def __handle_return(
        node: CDGNode,
        source_code_bytes,
        ast: Node,
        cdg: ControlDependenceGraph,
        break_nodes: List[CDGNode] = None,
        continue_nodes: List[CDGNode] = None) -> Tuple[List[CDGNode], List[CDGNode]]:
    if len(ast.children) > 2:
        entry_points = []
        siblings = __parse(
            source_code_bytes,
            ast.children[1],
            cdg,
            entry_points,
            break_nodes=break_nodes,
            continue_nodes=continue_nodes)
        siblings.append(node)
        __route_control_flow(entry_points, node, cdg)
    else:
        siblings = [node]
    return siblings, []


node_type_and_handler_map = {
    "variable_declarator":
        (CDG_NODE_TYPE_VARIABLE, __handle_node),
    "method_declaration":
        (CDG_NODE_TYPE_FUNCTION, __handle_method_declaration),
    "if_statement":
        (CDG_NODE_TYPE_BRANCH, __handle_if),
    "try_statement":
        (CDG_NODE_TYPE_BRANCH, __handle_try),
    "try_with_resources_statement":
        (CDG_NODE_TYPE_BRANCH, __handle_try),
    "catch_clause":
        (CDG_NODE_TYPE_BRANCH, __handle_catch),
    "while_statement":
        (CDG_NODE_TYPE_LOOP, __handle_for),
    "for_statement":
        (CDG_NODE_TYPE_LOOP, __handle_for),
    "enhanced_for_statement":
        (CDG_NODE_TYPE_LOOP, __handle_for_each),
    "assignment_expression":
        (CDG_NODE_TYPE_ASSIGNMENT, __handle_assignment),
    "method_invocation":
        (CDG_NODE_TYPE_CALL, __handle_node),
    "block":
        (CDG_NODE_TYPE_STATEMENTS, __handle_node),
    "continue_statement":
        (CDG_NODE_TYPE_GOTO, __handle_continue),
    "break_statement":
        (CDG_NODE_TYPE_GOTO, __handle_break),
    "return_statement":
        (CDG_NODE_TYPE_EXIT, __handle_return)
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
        entry_points: List[CDGNode],
        break_nodes: List[CDGNode] = None,
        continue_nodes: List[CDGNode] = None) -> List[CDGNode]:
    """
    Parse the tree_sitter ast into a Control Dependence Graph.
    :param ast: tree_sitter Node.
    :param cdg: Control Dependence Graph that will contain parsed nodes.
    :return: Control Dependence Graph Nodes that are siblings and should be placed instead of the given ast Node.
    """
    node_type, node_handler = __parse_node_type_and_handler(ast)
    start_point, end_point = __parse_position_range(ast)
    node = CDGNode(
        ast.type,
        node_type,
        start_point=start_point,
        end_point=end_point,
        name=__parse_node_name(source_code_bytes, ast))
    cdg.add_node(node)

    siblings, exit_nodes = node_handler(
        node,
        source_code_bytes,
        ast,
        cdg,
        break_nodes=break_nodes,
        continue_nodes=continue_nodes)
    if siblings:
        __route_control_flow(entry_points, siblings[0], cdg)
    entry_points.clear()
    for exit_node in exit_nodes:
        entry_points.append(exit_node)
    return siblings


def __parse_node_type_and_handler(ast: Node) -> Tuple[str, Callable]:
    return node_type_and_handler_map.get(ast.type, (CDG_NODE_TYPE_OBJECT, __handle_node))


def __parse_position_range(ast: Node) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    return ast.start_point, ast.end_point


def __parse_node_name(source_code_bytes: bytes, ast: Node) -> Optional[str]:
    if ast.type == "variable_declarator":
        return __parse_node_name(source_code_bytes, ast.child_by_field_name("name"))
    elif ast.type == "assignment_expression":
        return __parse_node_name(source_code_bytes, ast.child_by_field_name("left"))
    elif ast.start_point[0] == ast.end_point[0]:
        return source_code_bytes[ast.start_byte: ast.end_byte].decode("utf8")
    return None


def __route_control_flow(nodes_from: List[CDGNode], node_to: CDGNode, cdg: ControlDependenceGraph) -> None:
    for entry_point in nodes_from:
        if entry_point not in cdg.control_flow:
            cdg.control_flow[entry_point] = [node_to]
        else:
            cdg.control_flow[entry_point].append(node_to)

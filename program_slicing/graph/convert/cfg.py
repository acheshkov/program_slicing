__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/04/01'

import bisect
from typing import Dict, Set, List, Tuple, Optional

import networkx

from program_slicing.graph.cdg import ControlDependenceGraph
from program_slicing.graph.cfg import ControlFlowGraph
from program_slicing.graph.ddg import DataDependenceGraph
from program_slicing.graph.pdg import ProgramDependenceGraph
from program_slicing.graph.basic_block import BasicBlock
from program_slicing.graph.statement import Statement, StatementType, Point


def to_cdg(cfg: ControlFlowGraph) -> ControlDependenceGraph:
    """
    Convert the Control Flow Graph into a Control Dependence Graph.
    New graph will contain nodes, links on which where listed in the original one so that
    any changes made after converting in the original graph's statements will affect the converted one.
    :param cfg: Control Flow Graph that should to be converted.
    :return: Control Dependence Graph which nodes where contained in the Control Flow Graph on which it was based on.
    """
    raise NotImplementedError()


def to_ddg(cfg: ControlFlowGraph) -> DataDependenceGraph:
    """
    Convert the Control Flow Graph into a Data Dependence Graph.
    New graph will contain nodes, links on which where listed in the original one so that
    any changes made after converting in the original graph's statements will affect the converted one.
    :param cfg: Control Flow Graph that should to be converted.
    :return: Data Dependence Graph which nodes where contained in the Control Flow Graph on which it was based on.
    """
    ddg = DataDependenceGraph()
    visited: Dict[BasicBlock, Dict[str, Set[Statement]]] = {}
    variables: Dict[str, Set[Statement]] = {}
    for root in cfg.entry_points:
        __to_ddg(root, cfg=cfg, ddg=ddg, visited=visited, variables=variables)
        ddg.add_entry_point(root.root)
    __correct_scope_relations(ddg)
    return ddg


def to_pdg(cfg: ControlFlowGraph) -> ProgramDependenceGraph:
    """
    Convert the Control Flow Graph into a Program Dependence Graph.
    New graph will contain nodes, links on which where listed in the original one so that
    any changes made after converting in the original graph's statements will affect the converted one.
    :param cfg: Control Flow Graph that should to be converted.
    :return: Program Dependence Graph which nodes where contained in the Control Flow Graph on which it was based on.
    """
    raise NotImplementedError()


def __to_ddg(
        root: BasicBlock,
        cfg: ControlFlowGraph,
        ddg: DataDependenceGraph,
        visited: Dict[BasicBlock, Dict[str, Set[Statement]]],
        variables: Dict[str, Set[Statement]]) -> None:
    if root in visited:
        if not __update_variables(visited[root], variables):
            return
    else:
        visited[root] = {variable: variable_set.copy() for variable, variable_set in variables.items()}
    variables_entered: Dict[str, Set[Statement]] = visited[root]
    variables_passed: Dict[str, Set[Statement]] = {
        variable: variable_set for variable, variable_set in variables_entered.items()
    }
    for statement in root:
        ddg.add_node(statement)
        for affecting_variable_name in statement.affected_by:
            if statement.statement_type == StatementType.VARIABLE and affecting_variable_name == statement.name:
                continue
            if affecting_variable_name in variables_passed:
                for variable_statement in variables_passed[affecting_variable_name]:
                    ddg.add_edge(variable_statement, statement)
        if statement.statement_type == StatementType.VARIABLE or statement.statement_type == StatementType.ASSIGNMENT:
            variables_passed[statement.name] = {statement}
    for child in cfg.successors(root):
        __to_ddg(child, cfg=cfg, ddg=ddg, visited=visited, variables=variables_passed)


def __update_variables(old_variables: Dict[str, Set[Statement]], new_variables: Dict[str, Set[Statement]]) -> bool:
    updated = False
    for variable, variable_set in new_variables.items():
        if variable not in old_variables:
            old_variables[variable] = variable_set.copy()
            updated = True
        else:
            variable_entered_set = old_variables[variable]
            diff = variable_set.difference(variable_entered_set)
            variable_entered_set.update(diff)
            updated = len(diff) > 0
    return updated


def __correct_scope_relations(ddg: DataDependenceGraph) -> None:
    scope_for_statement: Dict[Statement, Statement] = __obtain_scope_hierarchy(ddg)
    variable_statements = [statement for statement in ddg if statement.statement_type == StatementType.VARIABLE]
    for variable_statement in variable_statements:
        if variable_statement not in scope_for_statement:
            continue
        variable_scope = scope_for_statement[variable_statement]
        remove_statements = []
        for statement in networkx.descendants(ddg, variable_statement):
            if statement.start_point < variable_scope.start_point or statement.end_point > variable_scope.end_point:
                remove_statements.append(statement)
        for statement in remove_statements:
            remove_edges = []
            for predecessor in ddg.predecessors(statement):
                if variable_scope.start_point <= predecessor.start_point and \
                        variable_scope.end_point >= predecessor.end_point:
                    remove_edges.append((predecessor, statement))
            ddg.remove_edges_from(remove_edges)


def __obtain_scope_hierarchy(ddg: DataDependenceGraph) -> Dict[Statement, Statement]:
    scopes_for_start_point: Dict[Point, Statement] = {}
    scopes_for_end_point: Dict[Point, Statement] = {}
    scopes: List[Statement] = sorted([
        statement for statement in ddg if
        statement.statement_type == StatementType.SCOPE or
        statement.statement_type == StatementType.GOTO or
        statement.statement_type == StatementType.BRANCH or
        statement.statement_type == StatementType.LOOP or
        statement.statement_type == StatementType.FUNCTION
    ], key=lambda statement: (
        statement.start_point,
        (-statement.end_point.line_number, -statement.end_point.column_number)
    ))
    points = []
    for scope in scopes:
        interval_start, interval_end = __obtain_interval(points, scope)
        if interval_start != scope.start_point:
            bisect.insort(points, scope.start_point)
            # insort is slow on array list, use linked list instead
            if interval_start in scopes_for_start_point:
                scopes_for_end_point[scope.start_point] = scopes_for_start_point[interval_start]
        if interval_end != scope.end_point:
            bisect.insort(points, scope.end_point)
            # insort is slow on array list, use linked list instead
            if interval_end in scopes_for_end_point:
                scopes_for_start_point[scope.end_point] = scopes_for_end_point[interval_end]
        scopes_for_start_point[scope.start_point] = scope
        scopes_for_end_point[scope.end_point] = scope
    result = {}
    for statement in ddg:
        interval_start, interval_end = __obtain_interval(points, statement)
        scope = None if (interval_start is None or interval_end is None) else \
            scopes_for_start_point.get(interval_start, None)
        if scope is not None:
            result[statement] = scope
    return result


def __obtain_interval(points: List[Point], statement: Statement) -> Tuple[Optional[Point], Optional[Point]]:
    nearest_start_point_id = bisect.bisect_right(points, statement.start_point) - 1
    nearest_start_point = None if nearest_start_point_id < 0 else points[nearest_start_point_id]
    nearest_end_point_id = bisect.bisect_left(points, statement.start_point)
    nearest_end_point = None if nearest_end_point_id >= len(points) else points[nearest_end_point_id]
    return nearest_start_point, nearest_end_point

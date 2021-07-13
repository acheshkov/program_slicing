__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/04/01'

from typing import Dict, Set

import networkx

from program_slicing.graph.cdg import ControlDependenceGraph
from program_slicing.graph.cfg import ControlFlowGraph
from program_slicing.graph.ddg import DataDependenceGraph
from program_slicing.graph.pdg import ProgramDependenceGraph
from program_slicing.graph.basic_block import BasicBlock
from program_slicing.graph.statement import Statement, StatementType


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
    ddg.set_scope_dependency(cfg.scope_dependency)
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
    variable_statements = [statement for statement in ddg if statement.statement_type == StatementType.VARIABLE]
    for variable_statement in variable_statements:
        if variable_statement not in ddg.scope_dependency:
            continue
        variable_scope = ddg.scope_dependency[variable_statement]
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

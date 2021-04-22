__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/04/01'

from typing import Dict, Set

from program_slicing.graph.cdg import ControlDependenceGraph
from program_slicing.graph.cfg import ControlFlowGraph
from program_slicing.graph.ddg import DataDependenceGraph
from program_slicing.graph.pdg import ProgramDependenceGraph
from program_slicing.graph.basic_block import BasicBlock
from program_slicing.graph.cdg_node import \
    CDG_NODE_TYPE_VARIABLE, \
    CDG_NODE_TYPE_ASSIGNMENT


def to_cdg(cfg: ControlFlowGraph) -> ControlDependenceGraph:
    """
    Convert the Control Flow Graph into a Control Dependence Graph.
    New graph will contain nodes, links on which where listed in the original one so that
    any changes made after converting in the original graph's content will affect the converted one.
    :param cfg: Control Flow Graph that should to be converted.
    :return: Control Dependence Graph which nodes where contained in the Control Flow Graph on which it was based on.
    """
    raise NotImplementedError()


def to_ddg(cfg: ControlFlowGraph) -> DataDependenceGraph:
    """
    Convert the Control Flow Graph into a Data Dependence Graph.
    New graph will contain same nodes as in the original one so that
    any changes made after converting in the original graph's content will affect the converted one.
    :param cfg: Control Flow Graph that should to be converted.
    :return: Data Dependence Graph which nodes where presented in the Control Flow Graph on which it was based on.
    """
    ddg = DataDependenceGraph()
    visited: Dict[BasicBlock, Dict[str, Set[BasicBlock]]] = {}
    variables: Dict[str, Set[BasicBlock]] = {}
    for root in cfg.get_entry_points():
        __to_ddg(root, cfg=cfg, ddg=ddg, visited=visited, variables=variables)
        ddg.add_entry_point(root)
    return ddg


def to_pdg(cfg: ControlFlowGraph) -> ProgramDependenceGraph:
    """
    Convert the Control Flow Graph into a Program Dependence Graph.
    New graph will contain same nodes as in the original one so that
    any changes made after converting in the original graph's content will affect the converted one.
    :param cfg: Control Flow Graph that should to be converted.
    :return: Program Dependence Graph which nodes where presented in the Control Flow Graph on which it was based on.
    """
    raise NotImplementedError()


def __to_ddg(
        root: BasicBlock,
        cfg: ControlFlowGraph,
        ddg: DataDependenceGraph,
        visited: Dict[BasicBlock, Dict[str, Set[BasicBlock]]],
        variables: Dict[str, Set[BasicBlock]]) -> None:
    if root in visited:
        if not __update_variables(visited[root], variables):
            return
    else:
        visited[root] = {variable: variable_set.copy() for variable, variable_set in variables.items()}
        ddg.add_node(root)
    variables_entered: Dict[str, Set[BasicBlock]] = visited[root]
    variables_passed: Dict[str, Set[BasicBlock]] = {
        variable: variable_set for variable, variable_set in variables_entered.items()
    }
    for node in root.get_content():
        if node.name in variables_entered:
            for variable_block in variables_entered[node.name]:
                ddg.add_edge(variable_block, root)
        if node.node_type == CDG_NODE_TYPE_VARIABLE or node.node_type == CDG_NODE_TYPE_ASSIGNMENT:
            variables_passed[node.name] = {root}
    for child in cfg.successors(root):
        __to_ddg(child, cfg=cfg, ddg=ddg, visited=visited, variables=variables_passed)


def __update_variables(old_variables: Dict[str, Set[BasicBlock]], new_variables: Dict[str, Set[BasicBlock]]) -> bool:
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

__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/04/01'

from typing import Dict, Set, List

from program_slicing.graph.cdg import ControlDependenceGraph
from program_slicing.graph.cfg import ControlFlowGraph
from program_slicing.graph.ddg import DataDependenceGraph
from program_slicing.graph.basic_block import BasicBlock
from program_slicing.graph.cdg_node import CDGNode, \
    CDG_NODE_TYPE_VARIABLE, \
    CDG_NODE_TYPE_ASSIGNMENT


def to_cfg(cdg: ControlDependenceGraph) -> ControlFlowGraph:
    """
    Convert the Control Dependence Graph into a Control Flow Graph.
    New graph will contain links on nodes of the original one so that
    any changes made after converting in the original graph will affect the converted one.
    :param cdg: Control Dependence Graph that should to be converted.
    :return: Control Flow Graph which nodes contain nodes of the Control Dependence Graph on which it was based on.
    """
    cfg = ControlFlowGraph()
    block: Dict[CDGNode, BasicBlock] = {}
    for root in cdg.get_entry_points():
        __to_cfg(root, cdg=cdg, cfg=cfg, block=block)
    return cfg


def to_ddg(cdg: ControlDependenceGraph) -> DataDependenceGraph:
    """
    Convert the Control Dependence Graph into a Data Dependence Graph.
    New graph will contain links on nodes of the original one so that
    any changes made after converting in the original graph will affect the converted one.
    :param cdg: Control Dependence Graph that should to be converted.
    :return: Data Dependence Graph which nodes contain nodes of the Control Dependence Graph on which it was based on.
    """
    cfg = to_cfg(cdg)
    ddg = DataDependenceGraph()
    visited: Dict[BasicBlock, Dict[str, Set[BasicBlock]]] = {}
    variables: Dict[str, Set[BasicBlock]] = {}
    for root in cfg.get_entry_points():
        __to_ddg(root, cfg=cfg, ddg=ddg, visited=visited, variables=variables)
        ddg.add_entry_point(root)
    return ddg


def __to_cfg(
        cdg_node: CDGNode,
        cdg: ControlDependenceGraph,
        cfg: ControlFlowGraph,
        block: Dict[CDGNode, BasicBlock]) -> None:
    f_children: List[CDGNode] = cdg.control_flow.get(cdg_node, [])
    prev_block: BasicBlock = block.get(cdg_node, None)
    process_list: List[CDGNode] = []
    for child in f_children:
        if child in block:
            __process_loop(child, cfg, block, prev_block)
        elif len(f_children) > 1:
            new_block = BasicBlock(content=[child])
            cfg.add_node(new_block)
            if prev_block is None:
                cfg.add_entry_point(new_block)
            else:
                cfg.add_edge(prev_block, new_block)
            block[child] = new_block
            process_list.append(child)
        else:
            if prev_block is None:
                prev_block = BasicBlock()
                cfg.add_node(prev_block)
                cfg.add_entry_point(prev_block)
            prev_block.append(child)
            block[child] = prev_block
            process_list.append(child)
    for child in process_list:
        __to_cfg(child, cdg, cfg, block)


def __process_loop(
        child: CDGNode,
        cfg: ControlFlowGraph,
        block: Dict[CDGNode, BasicBlock],
        prev_block: BasicBlock) -> None:
    old_block: BasicBlock = block[child]
    index = old_block.content.index(child)
    if index == 0:
        if prev_block is not None:
            cfg.add_edge(prev_block, old_block)
        return
    new_block = BasicBlock(content=old_block.content[index:])
    old_block.content = old_block.content[:index]
    block[child] = new_block
    cfg.add_node(new_block)
    old_successors: List[BasicBlock] = [successor for successor in cfg.successors(old_block)]
    for old_successor in old_successors:
        cfg.remove_edge(old_block, old_successor)
        cfg.add_edge(new_block, old_successor)
    cfg.add_edge(old_block, new_block)
    if prev_block is not None:
        cfg.add_edge(prev_block, new_block)


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
            if diff:
                for variable_block in diff:
                    variable_entered_set.add(variable_block)
                updated = True
    return updated

__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/04/01'

from typing import Dict, List

from program_slicing.graph.cdg import ControlDependenceGraph
from program_slicing.graph.cfg import ControlFlowGraph
from program_slicing.graph.ddg import DataDependenceGraph
from program_slicing.graph.pdg import ProgramDependenceGraph
from program_slicing.graph.basic_block import BasicBlock
from program_slicing.graph.cdg_node import CDGNode
from program_slicing.graph.convert.cfg import to_ddg as cfg_to_ddg


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
    return cfg_to_ddg(cfg)


def to_pdg(cdg: ControlDependenceGraph) -> ProgramDependenceGraph:
    """
    Convert the Control Dependence Graph into a Program Dependence Graph.
    New graph will contain links on nodes of the original one so that
    any changes made after converting in the original graph will affect the converted one.
    :param cdg: Control Dependence Graph that should to be converted.
    :return: Program Dependence Graph which nodes contain nodes of the original Control Dependence Graph.
    """
    ddg = to_ddg(cdg)
    pdg = ProgramDependenceGraph()
    block: Dict[CDGNode, BasicBlock] = {}
    for node in ddg:
        for cdg_node in node.get_content():
            block[cdg_node] = node
    for node in ddg:
        __to_pdg(node, cdg=cdg, ddg=ddg, pdg=pdg, block=block)
    for entry_point in ddg.get_entry_points():
        pdg.add_entry_point(entry_point)
    return pdg


def __to_pdg(
        node: BasicBlock,
        cdg: ControlDependenceGraph,
        ddg: DataDependenceGraph,
        pdg: ProgramDependenceGraph,
        block: Dict[CDGNode, BasicBlock]) -> None:
    pdg.add_node(node)
    for successor in ddg.successors(node):
        pdg.add_edge(node, successor)
    dom_set = set()
    for cdg_node in node.get_content():
        for successor in cdg.successors(cdg_node):
            if successor in block:
                dom_set.add(block[successor])
    for successor in dom_set:
        if successor != node:
            pdg.add_edge(node, successor)


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

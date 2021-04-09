__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/04/01'

from typing import Dict

from program_slicing.graph.cdg import ControlDependenceGraph
from program_slicing.graph.cfg import ControlFlowGraph
from program_slicing.graph.cdg_node import CDGNode
from program_slicing.graph.cfg_node import CFGNode


def to_cfg(cdg: ControlDependenceGraph) -> ControlFlowGraph:
    """
    Convert the Control Dependence Graph into a Control Flow Graph.
    New graph will contain links on nodes of the original one so that
    any changes made after converting in the original graph will affect the converted one.
    :param cdg: Control Dependence Graph that should to be converted.
    :return: Control Flow Graph which nodes contain nodes of the Control Dependence Graph on which it was based on.
    """
    cfg = ControlFlowGraph()
    block: Dict[CDGNode, CFGNode] = {}
    for root in cdg.get_entry_points():
        __to_cfg(root, cdg=cdg, cfg=cfg, block=block)
    return cfg


def __to_cfg(
        cdg_node: CDGNode,
        cdg: ControlDependenceGraph,
        cfg: ControlFlowGraph,
        block: Dict[CDGNode, CFGNode]) -> None:
    cfg_children = cdg.control_flow.get(cdg_node, [])
    prev_block = block.get(cdg_node, None)
    process_list = []
    if len(cfg_children) > 1:
        for child in cfg_children:
            if child in block:
                __process_loop(child, cfg, block, prev_block)
            else:
                new_block = CFGNode(content=[child])
                cfg.add_node(new_block)
                if prev_block is None:
                    cfg.add_entry_point(new_block)
                else:
                    cfg.add_edge(prev_block, new_block)
                block[child] = new_block
                process_list.append(child)
    else:
        for child in cfg_children:
            if child in block:
                __process_loop(child, cfg, block, prev_block)
            else:
                if prev_block is None:
                    prev_block = CFGNode()
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
        block: Dict[CDGNode, CFGNode],
        prev_block: CFGNode) -> None:
    old_block = block[child]
    index = old_block.content.index(child)
    if index == 0:
        if prev_block is not None:
            cfg.add_edge(prev_block, old_block)
        return
    new_block = CFGNode(content=old_block.content[index:])
    old_block.content = old_block.content[:index]
    block[child] = new_block
    cfg.add_node(new_block)
    old_successors = [successor for successor in cfg.successors(old_block)]
    for old_successor in old_successors:
        cfg.remove_edge(old_block, old_successor)
        cfg.add_edge(new_block, old_successor)
    cfg.add_edge(old_block, new_block)
    if prev_block is not None:
        cfg.add_edge(prev_block, new_block)

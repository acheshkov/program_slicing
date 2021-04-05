__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/04/01'

from typing import List
from program_slicing.graph.cdg import ControlDependenceGraph
from program_slicing.graph.cfg import ControlFlowGraph
from program_slicing.graph.cdg_node import CDGNode
from program_slicing.graph.cfg_node import CFGNode
from program_slicing.graph.cdg_node import \
    CDG_NODE_TYPE_BRANCH, \
    CDG_NODE_TYPE_LOOP


def to_cfg(cdg: ControlDependenceGraph) -> ControlFlowGraph:
    """
    Convert the Control Dependence Graph into a Control Flow Graph.
    Any changes in the original graph after converting will affect the converted one.
    :param cdg: Control Dependence Graph that should to be converted.
    :return: Control Flow Graph
    """
    cfg = ControlFlowGraph()
    for root in cdg.get_entry_points():
        __to_cfg(root, cdg=cdg, cfg=cfg)
    return cfg


def __to_cfg(cdg_node: CDGNode, cdg: ControlDependenceGraph, cfg: ControlFlowGraph) -> None:
    node_type = cdg_node.node_type
    children = [child for child in cdg.successors(cdg_node)]
    if node_type == CDG_NODE_TYPE_BRANCH:
        __to_cfg_block_branch(children, cfg)
    elif node_type == CDG_NODE_TYPE_LOOP:
        __to_cfg_block_loop(children, cfg)


def __to_cfg_block_branch(children: List[CDGNode], cfg: ControlFlowGraph) -> None:
    condition_block = CFGNode(
        content=[children[0]])
    true_block = CFGNode(
        content=[children[-1]])
    cfg.add_node(condition_block)
    cfg.add_node(true_block)
    cfg.add_edge(condition_block, true_block)
    if len(children) == 3:
        false_block = CFGNode(
            content=[children[-2]])
        cfg.add_node(false_block)
        cfg.add_edge(condition_block, false_block)


def __to_cfg_block_loop(children: List[CDGNode], cfg: ControlFlowGraph) -> None:
    condition_block = CFGNode(
        content=[children[0]])
    body_block = CFGNode(
        content=[children[-1]])
    cfg.add_node(condition_block)
    cfg.add_node(body_block)
    cfg.add_edge(condition_block, body_block)
    cfg.add_edge(body_block, condition_block)

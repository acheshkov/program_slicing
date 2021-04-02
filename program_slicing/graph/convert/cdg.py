__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/04/01'

from typing import List
from program_slicing.graph.cdg import ControlDependenceGraph
from program_slicing.graph.cfg import ControlFlowGraph
from program_slicing.graph.cdg_content import CDGContent
from program_slicing.graph.cfg_content import CFGContent
from program_slicing.graph.cdg_content import \
    CDG_CONTENT_TYPE_BRANCH, \
    CDG_CONTENT_TYPE_LOOP


def to_cfg(cdg: ControlDependenceGraph) -> ControlFlowGraph:
    """
    Convert the Control Dependence Graph into a Control Flow Graph.
    Any changes in the original graph after converting will affect the converted one.
    :param cdg: Control Dependence Graph that should to be converted.
    :return: Control Flow Graph
    """
    cfg = ControlFlowGraph()
    for root in cdg.get_roots():
        __to_cfg(root, cdg=cdg, cfg=cfg)
    return cfg


def __to_cfg(cdg_content: CDGContent, cdg: ControlDependenceGraph, cfg: ControlFlowGraph) -> None:
    content_type = cdg_content.content_type
    children = [child for child in cdg.successors(cdg_content)]
    if content_type == CDG_CONTENT_TYPE_BRANCH:
        __to_cfg_block_branch(children, cfg)
    elif content_type == CDG_CONTENT_TYPE_LOOP:
        __to_cfg_block_loop(children, cfg)


def __to_cfg_block_branch(children: List[CDGContent], cfg: ControlFlowGraph) -> None:
    condition_block = CFGContent(
        content=[children[0]])
    true_block = CFGContent(
        content=[children[-1]])
    cfg.add_node(condition_block)
    cfg.add_node(true_block)
    cfg.add_edge(condition_block, true_block)
    if len(children) == 3:
        false_block = CFGContent(
            content=[children[-2]])
        cfg.add_node(false_block)
        cfg.add_edge(condition_block, false_block)


def __to_cfg_block_loop(children: List[CDGContent], cfg: ControlFlowGraph) -> None:
    condition_block = CFGContent(
        content=[children[0]])
    body_block = CFGContent(
        content=[children[-1]])
    cfg.add_node(condition_block)
    cfg.add_node(body_block)
    cfg.add_edge(condition_block, body_block)
    cfg.add_edge(body_block, condition_block)

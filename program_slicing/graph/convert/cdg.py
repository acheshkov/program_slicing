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
from program_slicing.graph.statement import Statement
from program_slicing.graph.convert.cfg import to_ddg as cfg_to_ddg


def to_cfg(cdg: ControlDependenceGraph) -> ControlFlowGraph:
    """
    Convert the Control Dependence Graph into a Control Flow Graph.
    New graph will contain links on nodes of the original one so that
    any changes made after converting in the original graph's statements will affect the converted one.
    :param cdg: Control Dependence Graph that should to be converted.
    :return: Control Flow Graph which nodes contain nodes of the Control Dependence Graph on which it was based on.
    """
    cfg = ControlFlowGraph()
    block: Dict[Statement, BasicBlock] = {}
    for root in cdg.entry_points:
        __to_cfg(root, cdg=cdg, cfg=cfg, block=block)
    cfg.set_scope_dependency(cdg.scope_dependency)
    return cfg


def to_ddg(cdg: ControlDependenceGraph) -> DataDependenceGraph:
    """
    Convert the Control Dependence Graph into a Data Dependence Graph.
    New graph will contain same nodes as in the original one so that
    any changes made after converting in the original graph's statements will affect the converted one.
    :param cdg: Control Dependence Graph that should to be converted.
    :return: Data Dependence Graph which nodes where presented in the Control Dependence Graph on which it was based on.
    """
    cfg = to_cfg(cdg)
    return cfg_to_ddg(cfg)


def to_pdg(cdg: ControlDependenceGraph) -> ProgramDependenceGraph:
    """
    Convert the Control Dependence Graph into a Program Dependence Graph.
    New graph will contain same nodes as in the original one so that
    any changes made after converting in the original graph's statements will affect the converted one.
    :param cdg: Control Dependence Graph that should to be converted.
    :return: Program Dependence Graph which nodes where presented in the original Control Dependence Graph.
    """
    ddg = to_ddg(cdg)
    pdg = ProgramDependenceGraph()
    for node in cdg:
        pdg.add_node(node)
        for cdg_successor in cdg.successors(node):
            pdg.add_edge(node, cdg_successor)
        if node in ddg:
            for ddg_successor in ddg.successors(node):
                pdg.add_edge(node, ddg_successor)
    for entry_point in cdg.entry_points:
        pdg.add_entry_point(entry_point)
    pdg.set_scope_dependency(cdg.scope_dependency)
    return pdg


def __to_cfg(
        statement: Statement,
        cdg: ControlDependenceGraph,
        cfg: ControlFlowGraph,
        block: Dict[Statement, BasicBlock]) -> None:
    f_children: List[Statement] = cdg.control_flow.get(statement, [])
    prev_block: BasicBlock = block.get(statement, None)
    process_list: List[Statement] = []
    for child in f_children:
        if child in block:
            __process_loop(child, cfg, block, prev_block)
        elif len(f_children) > 1:
            new_block = BasicBlock(statements=[child])
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
        child: Statement,
        cfg: ControlFlowGraph,
        block: Dict[Statement, BasicBlock],
        prev_block: BasicBlock) -> None:
    old_block: BasicBlock = block[child]
    index = old_block.statements.index(child)
    if index == 0:
        if prev_block is not None:
            cfg.add_edge(prev_block, old_block)
        return
    new_block = old_block.split(index)
    for new_block_statement in new_block.statements:
        block[new_block_statement] = new_block
    cfg.add_node(new_block)
    old_successors: List[BasicBlock] = [successor for successor in cfg.successors(old_block)]
    for old_successor in old_successors:
        cfg.remove_edge(old_block, old_successor)
        cfg.add_edge(new_block, old_successor)
    cfg.add_edge(old_block, new_block)
    if prev_block is not None:
        cfg.add_edge(prev_block, new_block)

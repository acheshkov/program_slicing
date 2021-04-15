__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/04/02'

from unittest import TestCase

import networkx

from program_slicing.graph.cdg import ControlDependenceGraph
from program_slicing.graph.cfg import ControlFlowGraph
from program_slicing.graph import convert
from program_slicing.graph.cfg_node import CFGNode
from program_slicing.graph.cdg_node import CDGNode, \
    CDG_NODE_TYPE_FUNCTION, \
    CDG_NODE_TYPE_VARIABLE, \
    CDG_NODE_TYPE_ASSIGNMENT, \
    CDG_NODE_TYPE_BRANCH, \
    CDG_NODE_TYPE_GOTO, \
    CDG_NODE_TYPE_LOOP, \
    CDG_NODE_TYPE_STATEMENTS, \
    CDG_NODE_TYPE_OBJECT, \
    CDG_NODE_TYPE_EXIT


class CDGTestCase(TestCase):

    @staticmethod
    def __get_cdg_and_cfg_0():
        entry_point = CDGNode("", CDG_NODE_TYPE_FUNCTION, (0, 0), (0, 1), name="foo")
        variable_a = CDGNode("", CDG_NODE_TYPE_VARIABLE, (1, 1), (1, 2), name="a")
        variable_b = CDGNode("", CDG_NODE_TYPE_VARIABLE, (2, 2), (2, 3), name="b")
        loop = CDGNode("", CDG_NODE_TYPE_LOOP, (3, 3), (3, 4))
        assign_a = CDGNode("", CDG_NODE_TYPE_ASSIGNMENT, (4, 4), (4, 5), name="a")
        branch = CDGNode("", CDG_NODE_TYPE_BRANCH, (5, 5), (5, 6))
        statements = CDGNode("", CDG_NODE_TYPE_STATEMENTS, (6, 7), (6, 8))
        obj_0 = CDGNode("", CDG_NODE_TYPE_OBJECT, (6, 6), (6, 7))
        goto = CDGNode("", CDG_NODE_TYPE_GOTO, (7, 7), (7, 8))
        assign_b = CDGNode("", CDG_NODE_TYPE_ASSIGNMENT, (8, 8), (8, 9), name="b")
        obj_1 = CDGNode("", CDG_NODE_TYPE_OBJECT, (9, 9), (9, 10))
        exit_node = CDGNode("", CDG_NODE_TYPE_EXIT, (10, 10), (10, 11))

        cdg = ControlDependenceGraph()
        cdg.add_node(entry_point)
        cdg.add_node(variable_a)
        cdg.add_node(variable_b)
        cdg.add_node(loop)
        cdg.add_node(assign_a)
        cdg.add_node(branch)
        cdg.add_node(statements)
        cdg.add_node(obj_0)
        cdg.add_node(goto)
        cdg.add_node(assign_b)
        cdg.add_node(obj_1)
        cdg.add_node(exit_node)

        cdg.add_edge(entry_point, variable_a)
        cdg.add_edge(entry_point, variable_b)
        cdg.add_edge(entry_point, loop)
        cdg.add_edge(loop, assign_a)
        cdg.add_edge(loop, branch)
        cdg.add_edge(branch, statements)
        cdg.add_edge(branch, obj_0)
        cdg.add_edge(branch, goto)
        cdg.add_edge(branch, assign_b)
        cdg.add_edge(loop, obj_1)
        cdg.add_edge(entry_point, exit_node)
        cdg.control_flow = {
            entry_point: [variable_a],
            variable_a: [variable_b],
            variable_b: [loop],
            loop: [assign_a, exit_node],
            assign_a: [branch],
            branch: [statements, assign_b],
            statements: [obj_0],
            obj_0: [goto],
            goto: [loop],
            assign_b: [obj_1],
            obj_1: [loop]
        }
        cdg.add_entry_point(entry_point)

        block_0 = CFGNode([variable_a, variable_b])
        block_1 = CFGNode([loop])
        block_2 = CFGNode([assign_a, branch])
        block_3 = CFGNode([statements, obj_0, goto])
        block_4 = CFGNode([assign_b, obj_1])
        block_5 = CFGNode([exit_node])

        cfg = ControlFlowGraph()
        cfg.add_node(block_0)
        cfg.add_node(block_1)
        cfg.add_node(block_2)
        cfg.add_node(block_3)
        cfg.add_node(block_4)
        cfg.add_node(block_5)
        cfg.add_edge(block_0, block_1)
        cfg.add_edge(block_1, block_2)
        cfg.add_edge(block_2, block_3)
        cfg.add_edge(block_2, block_4)
        cfg.add_edge(block_3, block_1)
        cfg.add_edge(block_4, block_1)
        cfg.add_edge(block_1, block_5)
        cfg.add_entry_point(block_0)

        return cdg, cfg

    def test_convert_cdg_to_cfg_isomorphic(self):
        cdg, cfg = self.__get_cdg_and_cfg_0()
        self.assertTrue(networkx.is_isomorphic(cfg, convert.cdg.to_cfg(cdg)))

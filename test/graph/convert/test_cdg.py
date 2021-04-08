__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/04/02'

from unittest import TestCase

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
        entry_point = CDGNode("", CDG_NODE_TYPE_FUNCTION, (0, 0), name="foo")
        variable_a = CDGNode("", CDG_NODE_TYPE_VARIABLE, (1, 1), name="a")
        variable_b = CDGNode("", CDG_NODE_TYPE_VARIABLE, (2, 2), name="b")
        loop = CDGNode("", CDG_NODE_TYPE_LOOP, (3, 3))
        assign_a = CDGNode("", CDG_NODE_TYPE_ASSIGNMENT, (4, 4), name="a")
        branch = CDGNode("", CDG_NODE_TYPE_BRANCH, (5, 5))
        statements = CDGNode("", CDG_NODE_TYPE_STATEMENTS, (6, 7))
        obj_0 = CDGNode("", CDG_NODE_TYPE_OBJECT, (6, 6))
        goto = CDGNode("", CDG_NODE_TYPE_GOTO, (7, 7))
        assign_b = CDGNode("", CDG_NODE_TYPE_ASSIGNMENT, (7, 7), name="b")
        obj_1 = CDGNode("", CDG_NODE_TYPE_OBJECT, (8, 8))
        exit_node = CDGNode("", CDG_NODE_TYPE_EXIT, (9, 9))

        cdg = ControlDependenceGraph()
        cdg.add_nodes_from([
            entry_point,
            variable_a,
            variable_b,
            loop,
            assign_a,
            branch,
            statements,
            obj_0,
            goto,
            assign_b,
            obj_1,
            exit_node
        ])
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
        cfg.add_nodes_from([
            block_0,
            block_1,
            block_2,
            block_3,
            block_4,
            block_5,
        ])
        cfg.add_edge(block_0, block_1)
        cfg.add_edge(block_1, block_2)
        cfg.add_edge(block_2, block_3)
        cfg.add_edge(block_2, block_4)
        cfg.add_edge(block_3, block_1)
        cfg.add_edge(block_4, block_1)
        cfg.add_edge(block_1, block_5)
        cfg.add_entry_point(block_0)

        return cdg, cfg

    def __check_cfg_equality(
            self,
            cfg1: ControlFlowGraph,
            cfg2: ControlFlowGraph,
            root1: CFGNode = None,
            root2: CFGNode = None,
            visited=None):
        if root1 is None:
            entry_points_1 = {node for node in cfg1.get_entry_points()}
            if root2 is None:
                entry_points_2 = {node for node in cfg2.get_entry_points()}
            else:
                entry_points_2 = {root2}
            if visited is None:
                visited = set()
            self.assertEqual(len(entry_points_1), len(entry_points_2))
            self.assertTrue(len(entry_points_1) > 0)
            for entry_point_1, entry_point_2 in zip(entry_points_1, entry_points_2):
                self.__check_cfg_equality(cfg1, cfg2, entry_point_1, entry_point_2, visited)
        else:
            self.assertEqual(root1.content, root2.content)
            visited.add(root1)
            for child1, child2 in zip(cfg1.successors(root1), cfg2.successors(root2)):
                if child1 not in visited:
                    self.__check_cfg_equality(cfg1, cfg2, child1, child2, visited)

    def test_to_cfg(self):
        cdg, cfg = self.__get_cdg_and_cfg_0()
        self.__check_cfg_equality(cfg, convert.cdg.to_cfg(cdg))

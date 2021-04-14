__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/30'

from unittest import TestCase

import networkx

from program_slicing.graph.parse import cdg_java
from program_slicing.graph.cdg import ControlDependenceGraph
from program_slicing.graph.cdg_node import CDGNode, \
    CDG_NODE_TYPE_FUNCTION, \
    CDG_NODE_TYPE_VARIABLE, \
    CDG_NODE_TYPE_LOOP, \
    CDG_NODE_TYPE_ASSIGNMENT, \
    CDG_NODE_TYPE_BRANCH, \
    CDG_NODE_TYPE_STATEMENTS, \
    CDG_NODE_TYPE_CALL, \
    CDG_NODE_TYPE_OBJECT, \
    CDG_NODE_TYPE_GOTO, \
    CDG_NODE_TYPE_EXIT


class CDGJavaTestCase(TestCase):

    @staticmethod
    def __get_source_code_0():
        return """
        class A {
            public static int main() {
                int n = 10;
                for(int i = 0; i < n; i += 1) {
                    if (i < 4) {
                        System.out.println("lol");
                        continue;
                    }
                    if (i > 6) {
                        System.out.println("che bu rek");
                        break;
                    }
                    else
                        System.out.println("kek");
                }
                return n;
            }
        }
        """

    @staticmethod
    def __get_cdg_0():
        cdg = ControlDependenceGraph()
        roots = ["root_" + str(i) for i in range(8)]
        function_children = ["function_child_" + str(i) for i in range(24)]
        loop_children = ["loop_child_" + str(i) for i in range(24)]
        branch_1_children = ["branch_1_child_" + str(i) for i in range(17)]
        branch_2_children = ["branch_2_child_" + str(i) for i in range(30)]
        cdg.add_nodes_from(roots)
        cdg.add_nodes_from(function_children)
        cdg.add_nodes_from(loop_children)
        cdg.add_nodes_from(branch_1_children)
        cdg.add_nodes_from(branch_2_children)
        cdg.add_edges_from([("root_6", child) for child in function_children])
        cdg.add_edges_from([("function_child_22", child) for child in loop_children])
        cdg.add_edges_from([("loop_child_9", child) for child in branch_1_children])
        cdg.add_edges_from([("loop_child_17", child) for child in branch_2_children])
        return cdg

    def test_parse(self):
        cdg = cdg_java.parse(self.__get_source_code_0())
        self.assertEqual(104, len(cdg.nodes))
        entry_points = [entry_point for entry_point in cdg.entry_points]
        self.assertEqual(1, len(entry_points))
        self.assertEqual(CDG_NODE_TYPE_FUNCTION, entry_points[0].node_type)
        function_children = [child for child in cdg.successors(entry_points[0])]
        self.assertEqual(26, len(function_children))
        self.assertEqual(CDG_NODE_TYPE_STATEMENTS, function_children[0].node_type)
        self.assertEqual(CDG_NODE_TYPE_VARIABLE, function_children[5].node_type)
        self.assertEqual(CDG_NODE_TYPE_VARIABLE, function_children[13].node_type)
        self.assertEqual(CDG_NODE_TYPE_LOOP, function_children[22].node_type)
        self.assertEqual(CDG_NODE_TYPE_EXIT, function_children[24].node_type)
        loop_children = [child for child in cdg.successors(function_children[22])]
        self.assertEqual(23, len(loop_children))
        self.assertEqual(CDG_NODE_TYPE_STATEMENTS, loop_children[0].node_type)
        self.assertEqual(CDG_NODE_TYPE_BRANCH, loop_children[9].node_type)
        self.assertEqual(CDG_NODE_TYPE_BRANCH, loop_children[17].node_type)
        self.assertEqual(CDG_NODE_TYPE_ASSIGNMENT, loop_children[19].node_type)
        branch_1_children = [child for child in cdg.successors(loop_children[9])]
        self.assertEqual(17, len(branch_1_children))
        self.assertEqual(CDG_NODE_TYPE_STATEMENTS, branch_1_children[0].node_type)
        self.assertEqual(CDG_NODE_TYPE_CALL, branch_1_children[3].node_type)
        self.assertEqual(CDG_NODE_TYPE_GOTO, branch_1_children[15].node_type)
        branch_2_children = [child for child in cdg.successors(loop_children[17])]
        self.assertEqual(30, len(branch_2_children))
        self.assertEqual(CDG_NODE_TYPE_STATEMENTS, branch_2_children[0].node_type)
        self.assertEqual(CDG_NODE_TYPE_CALL, branch_2_children[3].node_type)
        self.assertEqual(CDG_NODE_TYPE_GOTO, branch_2_children[15].node_type)
        self.assertEqual(CDG_NODE_TYPE_CALL, branch_2_children[18].node_type)

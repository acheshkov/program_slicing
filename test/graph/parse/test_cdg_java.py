__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/30'

from unittest import TestCase

from program_slicing.graph.parse import cdg_java
from program_slicing.graph.cdg_node import \
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

    def check_cdg_children(self, children, node_type_map):
        for i, child in enumerate(children):
            node_type = node_type_map.get(i, CDG_NODE_TYPE_OBJECT)
            self.assertEqual(node_type, child.node_type)

    def test_while(self):
        source_code = """
        class A {
            int main() {
                while (1) {
                }
            }
        }
        """
        cdg = cdg_java.parse(source_code)
        self.assertEqual(19, len(cdg.nodes))
        entry_points = [entry_point for entry_point in cdg.entry_points]
        self.assertEqual(1, len(entry_points))
        self.check_cdg_children(entry_points, {
            0: CDG_NODE_TYPE_FUNCTION
        })
        function_children = [child for child in cdg.successors(entry_points[0])]
        self.assertEqual(8, len(function_children))
        self.check_cdg_children(function_children, {
            0: CDG_NODE_TYPE_STATEMENTS,
            6: CDG_NODE_TYPE_LOOP
        })
        loop_children = [child for child in cdg.successors(function_children[6])]
        self.assertEqual(3, len(loop_children))
        self.check_cdg_children(loop_children, {
            0: CDG_NODE_TYPE_STATEMENTS
        })

    def test_for_each(self):
        source_code = """
        class A {
            int main(String word) {
                for (char a : word) {
                }
            }
        }
        """
        cdg = cdg_java.parse(source_code)
        self.assertEqual(20, len(cdg.nodes))
        entry_points = [entry_point for entry_point in cdg.entry_points]
        self.assertEqual(1, len(entry_points))
        self.check_cdg_children(entry_points, {
            0: CDG_NODE_TYPE_FUNCTION
        })
        function_children = [child for child in cdg.successors(entry_points[0])]
        self.assertEqual(9, len(function_children))
        self.check_cdg_children(function_children, {
            0: CDG_NODE_TYPE_STATEMENTS,
            2: CDG_NODE_TYPE_VARIABLE,
            7: CDG_NODE_TYPE_LOOP
        })
        loop_children = [child for child in cdg.successors(function_children[7])]
        self.assertEqual(3, len(loop_children))
        self.check_cdg_children(loop_children, {
            0: CDG_NODE_TYPE_STATEMENTS
        })

    def test_for_each_modifiers(self):
        source_code = """
        class A {
            int main(String word) {
                for (final char a : word) {
                }
            }
        }
        """
        cdg = cdg_java.parse(source_code)
        self.assertEqual(22, len(cdg.nodes))
        entry_points = [entry_point for entry_point in cdg.entry_points]
        self.assertEqual(1, len(entry_points))
        self.check_cdg_children(entry_points, {
            0: CDG_NODE_TYPE_FUNCTION
        })
        function_children = [child for child in cdg.successors(entry_points[0])]
        self.assertEqual(11, len(function_children))
        self.check_cdg_children(function_children, {
            0: CDG_NODE_TYPE_STATEMENTS,
            2: CDG_NODE_TYPE_VARIABLE,
            9: CDG_NODE_TYPE_LOOP
        })
        loop_children = [child for child in cdg.successors(function_children[9])]
        self.assertEqual(3, len(loop_children))
        self.check_cdg_children(loop_children, {
            0: CDG_NODE_TYPE_STATEMENTS
        })

    def test_parse(self):
        source_code = """
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
        cdg = cdg_java.parse(source_code)
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

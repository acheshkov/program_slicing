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

    def test_try_catch(self):
        source_code = """
        class A {
            int main(String args) {
                try {
                    a = args[10];
                }
                catch (Exception e) {
                    e.printStackTrace();
                }
                finally {
                    System.out.println("The 'try catch' is finished.");
                }
            }
        }
        """
        cdg = cdg_java.parse(source_code)
        self.assertEqual(60, len(cdg.nodes))
        entry_points = [entry_point for entry_point in cdg.entry_points]
        self.assertEqual(1, len(entry_points))
        self.check_cdg_children(entry_points, {
            0: CDG_NODE_TYPE_FUNCTION
        })
        function_children = [child for child in cdg.successors(entry_points[0])]
        self.assertEqual(35, len(function_children))
        self.check_cdg_children(function_children, {
            0: CDG_NODE_TYPE_STATEMENTS,
            2: CDG_NODE_TYPE_STATEMENTS,
            5: CDG_NODE_TYPE_ASSIGNMENT,
            15: CDG_NODE_TYPE_BRANCH,
            18: CDG_NODE_TYPE_STATEMENTS,
            21: CDG_NODE_TYPE_CALL,
        })
        try_children = [child for child in cdg.successors(function_children[15])]
        self.assertEqual(5, len(try_children))
        self.check_cdg_children(try_children, {
            0: CDG_NODE_TYPE_VARIABLE,
            4: CDG_NODE_TYPE_BRANCH
        })
        catch_children = [child for child in cdg.successors(try_children[4])]
        self.assertEqual(12, len(catch_children))
        self.check_cdg_children(catch_children, {
            0: CDG_NODE_TYPE_STATEMENTS,
            3: CDG_NODE_TYPE_CALL
        })

    def test_resourced_try_multi_catch(self):
        source_code = """
        class A {
            int main(String args) {
                try (int i = 10) {
                    a = args[i];
                }
                catch (MyException1 e) {
                    e.printStackTrace();
                }
                catch (MyException2 e) {
                }
            }
        }
        """
        cdg = cdg_java.parse(source_code)
        self.assertEqual(59, len(cdg.nodes))
        entry_points = [entry_point for entry_point in cdg.entry_points]
        self.assertEqual(1, len(entry_points))
        self.check_cdg_children(entry_points, {
            0: CDG_NODE_TYPE_FUNCTION
        })
        function_children = [child for child in cdg.successors(entry_points[0])]
        self.assertEqual(26, len(function_children))
        self.check_cdg_children(function_children, {
            0: CDG_NODE_TYPE_STATEMENTS,
            11: CDG_NODE_TYPE_STATEMENTS,
            14: CDG_NODE_TYPE_ASSIGNMENT,
            24: CDG_NODE_TYPE_BRANCH
        })
        try_children = [child for child in cdg.successors(function_children[24])]
        self.assertEqual(5, len(try_children))
        self.check_cdg_children(try_children, {
            0: CDG_NODE_TYPE_VARIABLE,
            4: CDG_NODE_TYPE_BRANCH
        })
        catch_1_children = [child for child in cdg.successors(try_children[4])]
        self.assertEqual(17, len(catch_1_children))
        self.check_cdg_children(catch_1_children, {
            0: CDG_NODE_TYPE_STATEMENTS,
            3: CDG_NODE_TYPE_CALL,
            12: CDG_NODE_TYPE_VARIABLE,
            16: CDG_NODE_TYPE_BRANCH
        })
        catch_2_children = [child for child in cdg.successors(catch_1_children[16])]
        self.assertEqual(3, len(catch_2_children))
        self.check_cdg_children(catch_2_children, {
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
        self.check_cdg_children(entry_points, {
            0: CDG_NODE_TYPE_FUNCTION
        })
        function_children = [child for child in cdg.successors(entry_points[0])]
        self.assertEqual(26, len(function_children))
        self.check_cdg_children(function_children, {
            0: CDG_NODE_TYPE_STATEMENTS,
            5: CDG_NODE_TYPE_VARIABLE,
            13: CDG_NODE_TYPE_VARIABLE,
            22: CDG_NODE_TYPE_LOOP,
            24: CDG_NODE_TYPE_EXIT
        })
        loop_children = [child for child in cdg.successors(function_children[22])]
        self.assertEqual(23, len(loop_children))
        self.check_cdg_children(loop_children, {
            0: CDG_NODE_TYPE_STATEMENTS,
            9: CDG_NODE_TYPE_BRANCH,
            17: CDG_NODE_TYPE_BRANCH,
            19: CDG_NODE_TYPE_ASSIGNMENT
        })
        branch_1_children = [child for child in cdg.successors(loop_children[9])]
        self.assertEqual(17, len(branch_1_children))
        self.check_cdg_children(branch_1_children, {
            0: CDG_NODE_TYPE_STATEMENTS,
            3: CDG_NODE_TYPE_CALL,
            15: CDG_NODE_TYPE_GOTO
        })
        branch_2_children = [child for child in cdg.successors(loop_children[17])]
        self.assertEqual(30, len(branch_2_children))
        self.check_cdg_children(branch_1_children, {
            0: CDG_NODE_TYPE_STATEMENTS,
            3: CDG_NODE_TYPE_CALL,
            15: CDG_NODE_TYPE_GOTO,
            18: CDG_NODE_TYPE_CALL
        })

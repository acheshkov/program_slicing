__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/30'

from unittest import TestCase

from program_slicing.graph.parse import cdg_java
from program_slicing.graph.statement import \
    STATEMENT_TYPE_FUNCTION, \
    STATEMENT_TYPE_VARIABLE, \
    STATEMENT_TYPE_LOOP, \
    STATEMENT_TYPE_ASSIGNMENT, \
    STATEMENT_TYPE_BRANCH, \
    STATEMENT_TYPE_STATEMENTS, \
    STATEMENT_TYPE_CALL, \
    STATEMENT_TYPE_OBJECT, \
    STATEMENT_TYPE_GOTO, \
    STATEMENT_TYPE_EXIT


class CDGJavaTestCase(TestCase):

    def __check_cdg_children(self, children, statement_type_map):
        for i, child in enumerate(children):
            statement_type = statement_type_map.get(i, STATEMENT_TYPE_OBJECT)
            self.assertEqual(statement_type, child.statement_type)

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
        self.__check_cdg_children(entry_points, {
            0: STATEMENT_TYPE_FUNCTION
        })
        function_children = [child for child in cdg.successors(entry_points[0])]
        self.assertEqual(8, len(function_children))
        self.__check_cdg_children(function_children, {
            0: STATEMENT_TYPE_STATEMENTS,
            6: STATEMENT_TYPE_LOOP
        })
        loop_children = [child for child in cdg.successors(function_children[6])]
        self.assertEqual(3, len(loop_children))
        self.__check_cdg_children(loop_children, {
            0: STATEMENT_TYPE_STATEMENTS
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
        self.__check_cdg_children(entry_points, {
            0: STATEMENT_TYPE_FUNCTION
        })
        function_children = [child for child in cdg.successors(entry_points[0])]
        self.assertEqual(9, len(function_children))
        self.__check_cdg_children(function_children, {
            0: STATEMENT_TYPE_STATEMENTS,
            2: STATEMENT_TYPE_VARIABLE,
            7: STATEMENT_TYPE_LOOP
        })
        loop_children = [child for child in cdg.successors(function_children[7])]
        self.assertEqual(3, len(loop_children))
        self.__check_cdg_children(loop_children, {
            0: STATEMENT_TYPE_STATEMENTS
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
        self.__check_cdg_children(entry_points, {
            0: STATEMENT_TYPE_FUNCTION
        })
        function_children = [child for child in cdg.successors(entry_points[0])]
        self.assertEqual(11, len(function_children))
        self.__check_cdg_children(function_children, {
            0: STATEMENT_TYPE_STATEMENTS,
            2: STATEMENT_TYPE_VARIABLE,
            9: STATEMENT_TYPE_LOOP
        })
        loop_children = [child for child in cdg.successors(function_children[9])]
        self.assertEqual(3, len(loop_children))
        self.__check_cdg_children(loop_children, {
            0: STATEMENT_TYPE_STATEMENTS
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
        self.__check_cdg_children(entry_points, {
            0: STATEMENT_TYPE_FUNCTION
        })
        function_children = [child for child in cdg.successors(entry_points[0])]
        self.assertEqual(35, len(function_children))
        self.__check_cdg_children(function_children, {
            0: STATEMENT_TYPE_STATEMENTS,
            2: STATEMENT_TYPE_STATEMENTS,
            5: STATEMENT_TYPE_ASSIGNMENT,
            15: STATEMENT_TYPE_BRANCH,
            18: STATEMENT_TYPE_STATEMENTS,
            21: STATEMENT_TYPE_CALL,
        })
        try_children = [child for child in cdg.successors(function_children[15])]
        self.assertEqual(5, len(try_children))
        self.__check_cdg_children(try_children, {
            0: STATEMENT_TYPE_VARIABLE,
            4: STATEMENT_TYPE_BRANCH
        })
        catch_children = [child for child in cdg.successors(try_children[4])]
        self.assertEqual(12, len(catch_children))
        self.__check_cdg_children(catch_children, {
            0: STATEMENT_TYPE_STATEMENTS,
            3: STATEMENT_TYPE_CALL
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
        self.__check_cdg_children(entry_points, {
            0: STATEMENT_TYPE_FUNCTION
        })
        function_children = [child for child in cdg.successors(entry_points[0])]
        self.assertEqual(26, len(function_children))
        self.__check_cdg_children(function_children, {
            0: STATEMENT_TYPE_STATEMENTS,
            11: STATEMENT_TYPE_STATEMENTS,
            14: STATEMENT_TYPE_ASSIGNMENT,
            24: STATEMENT_TYPE_BRANCH
        })
        try_children = [child for child in cdg.successors(function_children[24])]
        self.assertEqual(5, len(try_children))
        self.__check_cdg_children(try_children, {
            0: STATEMENT_TYPE_VARIABLE,
            4: STATEMENT_TYPE_BRANCH
        })
        catch_1_children = [child for child in cdg.successors(try_children[4])]
        self.assertEqual(17, len(catch_1_children))
        self.__check_cdg_children(catch_1_children, {
            0: STATEMENT_TYPE_STATEMENTS,
            3: STATEMENT_TYPE_CALL,
            12: STATEMENT_TYPE_VARIABLE,
            16: STATEMENT_TYPE_BRANCH
        })
        catch_2_children = [child for child in cdg.successors(catch_1_children[16])]
        self.assertEqual(3, len(catch_2_children))
        self.__check_cdg_children(catch_2_children, {
            0: STATEMENT_TYPE_STATEMENTS
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
        self.__check_cdg_children(entry_points, {
            0: STATEMENT_TYPE_FUNCTION
        })
        function_children = [child for child in cdg.successors(entry_points[0])]
        self.assertEqual(26, len(function_children))
        self.__check_cdg_children(function_children, {
            0: STATEMENT_TYPE_STATEMENTS,
            5: STATEMENT_TYPE_VARIABLE,
            13: STATEMENT_TYPE_VARIABLE,
            22: STATEMENT_TYPE_LOOP,
            24: STATEMENT_TYPE_EXIT
        })
        loop_children = [child for child in cdg.successors(function_children[22])]
        self.assertEqual(23, len(loop_children))
        self.__check_cdg_children(loop_children, {
            0: STATEMENT_TYPE_STATEMENTS,
            9: STATEMENT_TYPE_BRANCH,
            17: STATEMENT_TYPE_BRANCH,
            19: STATEMENT_TYPE_ASSIGNMENT
        })
        branch_1_children = [child for child in cdg.successors(loop_children[9])]
        self.assertEqual(17, len(branch_1_children))
        self.__check_cdg_children(branch_1_children, {
            0: STATEMENT_TYPE_STATEMENTS,
            3: STATEMENT_TYPE_CALL,
            15: STATEMENT_TYPE_GOTO
        })
        branch_2_children = [child for child in cdg.successors(loop_children[17])]
        self.assertEqual(30, len(branch_2_children))
        self.__check_cdg_children(branch_1_children, {
            0: STATEMENT_TYPE_STATEMENTS,
            3: STATEMENT_TYPE_CALL,
            15: STATEMENT_TYPE_GOTO,
            18: STATEMENT_TYPE_CALL
        })

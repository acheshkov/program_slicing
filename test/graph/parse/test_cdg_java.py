__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/30'

from typing import List, Dict
from unittest import TestCase

from program_slicing.graph.parse import cdg_java
from program_slicing.graph.statement import Statement, StatementType


class CDGJavaTestCase(TestCase):

    def __check_cdg_children(self, children: List[Statement], statement_type_map: Dict[int, StatementType]) -> None:
        for i, child in enumerate(children):
            statement_type = statement_type_map.get(i, StatementType.object)
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
        self.assertEqual(9, len(cdg.nodes))
        entry_points = [entry_point for entry_point in cdg.entry_points]
        self.assertEqual(1, len(entry_points))
        self.__check_cdg_children(entry_points, {
            0: StatementType.function
        })
        function_children = [child for child in cdg.successors(entry_points[0])]
        self.assertEqual(4, len(function_children))
        self.__check_cdg_children(function_children, {
            0: StatementType.statements,
            3: StatementType.loop
        })
        loop_children = [child for child in cdg.successors(function_children[3])]
        self.assertEqual(1, len(loop_children))
        self.__check_cdg_children(loop_children, {
            0: StatementType.statements
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
        self.assertEqual(11, len(cdg.nodes))
        entry_points = [entry_point for entry_point in cdg.entry_points]
        self.assertEqual(1, len(entry_points))
        self.__check_cdg_children(entry_points, {
            0: StatementType.function
        })
        function_children = [child for child in cdg.successors(entry_points[0])]
        self.assertEqual(6, len(function_children))
        self.__check_cdg_children(function_children, {
            0: StatementType.statements,
            1: StatementType.variable,
            5: StatementType.loop
        })
        loop_children = [child for child in cdg.successors(function_children[5])]
        self.assertEqual(1, len(loop_children))
        self.__check_cdg_children(loop_children, {
            0: StatementType.statements
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
        self.assertEqual(12, len(cdg.nodes))
        entry_points = [entry_point for entry_point in cdg.entry_points]
        self.assertEqual(1, len(entry_points))
        self.__check_cdg_children(entry_points, {
            0: StatementType.function
        })
        function_children = [child for child in cdg.successors(entry_points[0])]
        self.assertEqual(7, len(function_children))
        self.__check_cdg_children(function_children, {
            0: StatementType.statements,
            1: StatementType.variable,
            6: StatementType.loop
        })
        loop_children = [child for child in cdg.successors(function_children[6])]
        self.assertEqual(1, len(loop_children))
        self.__check_cdg_children(loop_children, {
            0: StatementType.statements
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
        self.assertEqual(31, len(cdg.nodes))
        entry_points = [entry_point for entry_point in cdg.entry_points]
        self.assertEqual(1, len(entry_points))
        self.__check_cdg_children(entry_points, {
            0: StatementType.function
        })
        function_children = [child for child in cdg.successors(entry_points[0])]
        self.assertEqual(18, len(function_children))
        self.__check_cdg_children(function_children, {
            0: StatementType.statements,
            1: StatementType.statements,
            7: StatementType.assignment,
            8: StatementType.branch,
            10: StatementType.statements,
            12: StatementType.call,
        })
        try_children = [child for child in cdg.successors(function_children[8])]
        self.assertEqual(4, len(try_children))
        self.__check_cdg_children(try_children, {
            0: StatementType.variable,
            3: StatementType.branch
        })
        catch_children = [child for child in cdg.successors(try_children[3])]
        self.assertEqual(5, len(catch_children))
        self.__check_cdg_children(catch_children, {
            0: StatementType.statements,
            2: StatementType.call
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
        self.assertEqual(31, len(cdg.nodes))
        entry_points = [entry_point for entry_point in cdg.entry_points]
        self.assertEqual(1, len(entry_points))
        self.__check_cdg_children(entry_points, {
            0: StatementType.function
        })
        function_children = [child for child in cdg.successors(entry_points[0])]
        self.assertEqual(13, len(function_children))
        self.__check_cdg_children(function_children, {
            0: StatementType.statements,
            5: StatementType.statements,
            11: StatementType.assignment,
            12: StatementType.branch
        })
        try_children = [child for child in cdg.successors(function_children[12])]
        self.assertEqual(4, len(try_children))
        self.__check_cdg_children(try_children, {
            0: StatementType.variable,
            3: StatementType.branch
        })
        catch_1_children = [child for child in cdg.successors(try_children[3])]
        self.assertEqual(9, len(catch_1_children))
        self.__check_cdg_children(catch_1_children, {
            0: StatementType.statements,
            2: StatementType.call,
            5: StatementType.variable,
            8: StatementType.branch
        })
        catch_2_children = [child for child in cdg.successors(catch_1_children[8])]
        self.assertEqual(1, len(catch_2_children))
        self.__check_cdg_children(catch_2_children, {
            0: StatementType.statements
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
        self.assertEqual(58, len(cdg.nodes))
        entry_points = [entry_point for entry_point in cdg.entry_points]
        self.assertEqual(1, len(entry_points))
        self.__check_cdg_children(entry_points, {
            0: StatementType.function
        })
        function_children = [child for child in cdg.successors(entry_points[0])]
        self.assertEqual(15, len(function_children))
        self.__check_cdg_children(function_children, {
            0: StatementType.statements,
            3: StatementType.variable,
            7: StatementType.variable,
            12: StatementType.loop,
            14: StatementType.exit
        })
        loop_children = [child for child in cdg.successors(function_children[12])]
        self.assertEqual(14, len(loop_children))
        self.__check_cdg_children(loop_children, {
            0: StatementType.statements,
            5: StatementType.branch,
            10: StatementType.branch,
            13: StatementType.assignment
        })
        branch_1_children = [child for child in cdg.successors(loop_children[5])]
        self.assertEqual(9, len(branch_1_children))
        self.__check_cdg_children(branch_1_children, {
            0: StatementType.statements,
            2: StatementType.call,
            8: StatementType.goto
        })
        branch_2_children = [child for child in cdg.successors(loop_children[10])]
        self.assertEqual(16, len(branch_2_children))
        self.__check_cdg_children(branch_1_children, {
            0: StatementType.statements,
            2: StatementType.call,
            8: StatementType.goto,
            10: StatementType.call
        })

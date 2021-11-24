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
            statement_type = statement_type_map.get(i, StatementType.UNKNOWN)
            self.assertEqual(statement_type, child.statement_type)

    def test_switch(self) -> None:
        source_code = """
        {
            switch(a) {
                default:
                    a = 1;
                case 10:
                    myFoo();
                case 5:
                    break;
                case 4:
                    a = -1;
        }
        """
        cdg = cdg_java.parse(source_code)
        self.assertEqual(23, len(cdg.nodes))
        entry_points = [entry_point for entry_point in cdg.entry_points]
        self.assertEqual(1, len(entry_points))
        self.__check_cdg_children(entry_points, {
            0: StatementType.FUNCTION
        })
        function_children = [child for child in cdg.successors(entry_points[0])]
        self.assertEqual(6, len(function_children))
        self.__check_cdg_children(function_children, {
            0: StatementType.SCOPE,
            3: StatementType.SCOPE,
            4: StatementType.BRANCH,
            5: StatementType.EXIT
        })
        branch_children = [child for child in cdg.successors(function_children[4])]
        self.assertEqual(16, len(branch_children))
        self.__check_cdg_children(branch_children, {
            0: StatementType.SCOPE,
            4: StatementType.ASSIGNMENT,
            5: StatementType.SCOPE,
            7: StatementType.CALL,
            8: StatementType.SCOPE,
            9: StatementType.GOTO,
            10: StatementType.SCOPE,
            15: StatementType.ASSIGNMENT
        })

    def test_while(self) -> None:
        source_code = """
        {
            while (1) {
            }
        }
        """
        cdg = cdg_java.parse(source_code)
        self.assertEqual(7, len(cdg.nodes))
        entry_points = [entry_point for entry_point in cdg.entry_points]
        self.assertEqual(1, len(entry_points))
        self.__check_cdg_children(entry_points, {
            0: StatementType.FUNCTION
        })
        function_children = [child for child in cdg.successors(entry_points[0])]
        self.assertEqual(5, len(function_children))
        self.__check_cdg_children(function_children, {
            0: StatementType.SCOPE,
            3: StatementType.LOOP,
            4: StatementType.EXIT
        })
        loop_children = [child for child in cdg.successors(function_children[3])]
        self.assertEqual(1, len(loop_children))
        self.__check_cdg_children(loop_children, {
            0: StatementType.SCOPE
        })

    def test_for_each(self) -> None:
        source_code = """
        class A {
            int main(String word) {
                for (char a : word) {
                }
            }
        }
        """
        cdg = cdg_java.parse(source_code)
        self.assertEqual(14, len(cdg.nodes))
        entry_points = [entry_point for entry_point in cdg.entry_points]
        self.assertEqual(1, len(entry_points))
        self.__check_cdg_children(entry_points, {
            0: StatementType.FUNCTION
        })
        function_children = [child for child in cdg.successors(entry_points[0])]
        self.assertEqual(9, len(function_children))
        self.__check_cdg_children(function_children, {
            1: StatementType.VARIABLE,
            2: StatementType.SCOPE,
            3: StatementType.VARIABLE,
            7: StatementType.LOOP,
            8: StatementType.EXIT
        })
        loop_children = [child for child in cdg.successors(function_children[7])]
        self.assertEqual(1, len(loop_children))
        self.__check_cdg_children(loop_children, {
            0: StatementType.SCOPE
        })

    def test_for_each_modifiers(self) -> None:
        source_code = """
        class A {
            int main(String word) {
                for (final char a : word) {
                }
            }
        }
        """
        cdg = cdg_java.parse(source_code)
        self.assertEqual(15, len(cdg.nodes))
        entry_points = [entry_point for entry_point in cdg.entry_points]
        self.assertEqual(1, len(entry_points))
        self.__check_cdg_children(entry_points, {
            0: StatementType.FUNCTION
        })
        function_children = [child for child in cdg.successors(entry_points[0])]
        self.assertEqual(10, len(function_children))
        self.__check_cdg_children(function_children, {
            1: StatementType.VARIABLE,
            2: StatementType.SCOPE,
            3: StatementType.VARIABLE,
            8: StatementType.LOOP,
            9: StatementType.EXIT
        })
        loop_children = [child for child in cdg.successors(function_children[8])]
        self.assertEqual(1, len(loop_children))
        self.__check_cdg_children(loop_children, {
            0: StatementType.SCOPE
        })

    def test_try_catch(self) -> None:
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
        self.assertEqual(25, len(cdg.nodes))
        entry_points = [entry_point for entry_point in cdg.entry_points]
        self.assertEqual(1, len(entry_points))
        self.__check_cdg_children(entry_points, {
            0: StatementType.FUNCTION
        })
        function_children = [child for child in cdg.successors(entry_points[0])]
        self.assertEqual(9, len(function_children))
        self.__check_cdg_children(function_children, {
            1: StatementType.VARIABLE,
            2: StatementType.SCOPE,
            3: StatementType.BRANCH,
            5: StatementType.SCOPE,
            7: StatementType.CALL,
            8: StatementType.EXIT
        })
        try_children = [child for child in cdg.successors(function_children[3])]
        self.assertEqual(9, len(try_children))
        self.__check_cdg_children(try_children, {
            0: StatementType.SCOPE,
            6: StatementType.ASSIGNMENT,
            7: StatementType.VARIABLE,
            8: StatementType.BRANCH
        })
        catch_children = [child for child in cdg.successors(try_children[8])]
        self.assertEqual(3, len(catch_children))
        self.__check_cdg_children(catch_children, {
            0: StatementType.SCOPE,
            2: StatementType.CALL
        })

    def test_resourced_try_multi_catch(self) -> None:
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
        self.assertEqual(28, len(cdg.nodes))
        entry_points = [entry_point for entry_point in cdg.entry_points]
        self.assertEqual(1, len(entry_points))
        self.__check_cdg_children(entry_points, {
            0: StatementType.FUNCTION
        })
        function_children = [child for child in cdg.successors(entry_points[0])]
        self.assertEqual(9, len(function_children))
        self.__check_cdg_children(function_children, {
            1: StatementType.VARIABLE,
            2: StatementType.SCOPE,
            7: StatementType.BRANCH,
            8: StatementType.EXIT
        })
        try_children = [child for child in cdg.successors(function_children[7])]
        self.assertEqual(9, len(try_children))
        self.__check_cdg_children(try_children, {
            0: StatementType.SCOPE,
            6: StatementType.ASSIGNMENT,
            7: StatementType.VARIABLE,
            8: StatementType.BRANCH
        })
        catch_1_children = [child for child in cdg.successors(try_children[8])]
        self.assertEqual(5, len(catch_1_children))
        self.__check_cdg_children(catch_1_children, {
            0: StatementType.SCOPE,
            2: StatementType.CALL,
            3: StatementType.VARIABLE,
            4: StatementType.BRANCH
        })
        catch_2_children = [child for child in cdg.successors(catch_1_children[4])]
        self.assertEqual(1, len(catch_2_children))
        self.__check_cdg_children(catch_2_children, {
            0: StatementType.SCOPE
        })

    def test_update(self) -> None:
        source_code = """
        {
            int n = 0;
            for (int i = 0; i < 10; i++) {
                ++n;
            }
        }
        """
        cdg = cdg_java.parse(source_code)
        self.assertEqual(19, len(cdg.nodes))
        entry_points = [entry_point for entry_point in cdg.entry_points]
        self.assertEqual(1, len(entry_points))
        self.__check_cdg_children(entry_points, {
            0: StatementType.FUNCTION
        })
        function_children = [child for child in cdg.successors(entry_points[0])]
        self.assertEqual(12, len(function_children))
        self.__check_cdg_children(function_children, {
            0: StatementType.SCOPE,
            3: StatementType.VARIABLE,
            6: StatementType.VARIABLE,
            10: StatementType.LOOP,
            11: StatementType.EXIT
        })
        loop_children = [child for child in cdg.successors(function_children[10])]
        self.assertEqual(6, len(loop_children))
        self.__check_cdg_children(loop_children, {
            0: StatementType.SCOPE,
            3: StatementType.ASSIGNMENT,
            5: StatementType.ASSIGNMENT
        })

    def test_multiple_returns(self) -> None:
        source_code = """
        {
            int n = 0;
            int a = 10;
            if (n < a) {
                return n;
            }
            return a;
        }
        """
        cdg = cdg_java.parse(source_code)
        self.assertEqual(19, len(cdg.nodes))
        entry_points = [entry_point for entry_point in cdg.entry_points]
        self.assertEqual(1, len(entry_points))
        self.__check_cdg_children(entry_points, {
            0: StatementType.FUNCTION
        })
        function_children = [child for child in cdg.successors(entry_points[0])]
        self.assertEqual(15, len(function_children))
        self.__check_cdg_children(function_children, {
            0: StatementType.SCOPE,
            3: StatementType.VARIABLE,
            6: StatementType.VARIABLE,
            11: StatementType.BRANCH,
            13: StatementType.GOTO,
            14: StatementType.EXIT
        })
        self.assertEqual({"a", "n"}, function_children[11].affected_by)
        branch_children = [child for child in cdg.successors(function_children[11])]
        self.assertEqual(3, len(branch_children))
        self.__check_cdg_children(branch_children, {
            0: StatementType.SCOPE,
            2: StatementType.GOTO
        })

    def test_synchronized(self) -> None:
        source_code = """
        {
            synchronized(a) {
                a = -1;
            }
        }
        """
        cdg = cdg_java.parse(source_code)
        self.assertEqual(12, len(cdg.nodes))
        entry_points = [entry_point for entry_point in cdg.entry_points]
        self.assertEqual(1, len(entry_points))
        self.__check_cdg_children(entry_points, {
            0: StatementType.FUNCTION
        })
        function_children = [child for child in cdg.successors(entry_points[0])]
        self.assertEqual(5, len(function_children))
        self.__check_cdg_children(function_children, {
            0: StatementType.SCOPE,
            3: StatementType.LOOP,
            4: StatementType.EXIT
        })
        loop_children = [child for child in cdg.successors(function_children[3])]
        self.assertEqual(6, len(loop_children))
        self.__check_cdg_children(loop_children, {
            0: StatementType.SCOPE,
            5: StatementType.ASSIGNMENT
        })

    def test_parse(self) -> None:
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
        self.assertEqual(44, len(cdg.nodes))
        entry_points = [entry_point for entry_point in cdg.entry_points]
        self.assertEqual(1, len(entry_points))
        self.__check_cdg_children(entry_points, {
            0: StatementType.FUNCTION
        })
        function_children = [child for child in cdg.successors(entry_points[0])]
        self.assertEqual(15, len(function_children))
        self.__check_cdg_children(function_children, {
            1: StatementType.SCOPE,
            4: StatementType.VARIABLE,
            7: StatementType.VARIABLE,
            11: StatementType.LOOP,
            13: StatementType.GOTO,
            14: StatementType.EXIT
        })
        loop_children = [child for child in cdg.successors(function_children[11])]
        self.assertEqual(14, len(loop_children))
        self.__check_cdg_children(loop_children, {
            0: StatementType.SCOPE,
            5: StatementType.BRANCH,
            10: StatementType.BRANCH,
            13: StatementType.ASSIGNMENT
        })
        branch_1_children = [child for child in cdg.successors(loop_children[5])]
        self.assertEqual(4, len(branch_1_children))
        self.__check_cdg_children(branch_1_children, {
            0: StatementType.SCOPE,
            2: StatementType.CALL,
            3: StatementType.GOTO
        })
        branch_2_children = [child for child in cdg.successors(loop_children[10])]
        self.assertEqual(7, len(branch_2_children))
        self.__check_cdg_children(branch_1_children, {
            0: StatementType.SCOPE,
            2: StatementType.CALL,
            3: StatementType.GOTO,
            4: StatementType.GOTO,
            6: StatementType.CALL
        })

    def test_parse_without_class(self) -> None:
        source_code = """
        public static int main(int arg) {
            int n = 10 + arg;
            return n;
        }
        """
        cdg = cdg_java.parse(source_code)
        self.assertEqual(10, len(cdg.nodes))
        entry_points = [entry_point for entry_point in cdg.entry_points]
        self.assertEqual(1, len(entry_points))
        self.__check_cdg_children(entry_points, {
            0: StatementType.FUNCTION
        })
        function_children = [child for child in cdg.successors(entry_points[0])]
        self.assertEqual(9, len(function_children))
        self.__check_cdg_children(function_children, {
            1: StatementType.VARIABLE,
            2: StatementType.SCOPE,
            5: StatementType.VARIABLE,
            7: StatementType.GOTO,
            8: StatementType.EXIT
        })

    def test_parse_without_function(self) -> None:
        source_code = """
        int n = 10 + arg;
        return n;
        """
        cdg = cdg_java.parse(source_code)
        self.assertEqual(7, len(cdg.nodes))
        entry_points = [entry_point for entry_point in cdg.entry_points]
        self.assertEqual(1, len(entry_points))
        self.__check_cdg_children(entry_points, {
            0: StatementType.FUNCTION
        })
        function_children = [child for child in cdg.successors(entry_points[0])]
        self.assertEqual(6, len(function_children))
        self.__check_cdg_children(function_children, {
            2: StatementType.VARIABLE,
            4: StatementType.GOTO,
            5: StatementType.EXIT
        })

    def test_parse_with_inner_functions(self) -> None:
        source_code = """
        class A {
            int main() {
                int n = 0;
                class B {
                    int gain() {
                        int k = 0;
                    }
                }
            }
        }
        """
        cdg = cdg_java.parse(source_code)
        self.assertEqual(19, len(cdg.nodes))
        entry_points = [entry_point for entry_point in cdg.entry_points]
        self.assertEqual(2, len(entry_points))
        self.__check_cdg_children(entry_points, {
            0: StatementType.FUNCTION,
            1: StatementType.FUNCTION
        })
        for entry_point in entry_points:
            function_children = [child for child in cdg.successors(entry_point)]
            if len(function_children) == 6:
                self.__check_cdg_children(function_children, {
                    1: StatementType.SCOPE,
                    4: StatementType.VARIABLE,
                    5: StatementType.EXIT
                })
            elif len(function_children) == 8:
                self.__check_cdg_children(function_children, {
                    1: StatementType.SCOPE,
                    4: StatementType.VARIABLE,
                    6: StatementType.SCOPE,
                    7: StatementType.EXIT
                })
            else:
                self.assertFalse(True)

    def test_parse_constructor(self) -> None:
        source_code = """
        class MyClass {
            int a;
            MyClass() {
                this.a = 0;
            }
        }
        """
        cdg = cdg_java.parse(source_code)
        self.assertEqual(16, len(cdg.nodes))
        entry_points = [entry_point for entry_point in cdg.entry_points]
        self.assertEqual(1, len(entry_points))
        self.__check_cdg_children(entry_points, {
            0: StatementType.FUNCTION
        })
        function_children = [child for child in cdg.successors(entry_points[0])]
        self.assertEqual(9, len(function_children))
        self.__check_cdg_children(function_children, {
            1: StatementType.SCOPE,
            7: StatementType.ASSIGNMENT,
            8: StatementType.EXIT
        })

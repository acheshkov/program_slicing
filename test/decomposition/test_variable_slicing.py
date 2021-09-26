__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/22'

from unittest import TestCase

from program_slicing.decomposition import variable_slicing
from program_slicing.decomposition.slice_predicate import SlicePredicate
from program_slicing.decomposition.variable_slicing import get_variable_slices
from program_slicing.graph.parse import LANG_JAVA
from program_slicing.graph.statement import Statement, StatementType
from program_slicing.graph.point import Point
from program_slicing.graph.manager import ProgramGraphsManager

is_slicing_criterion = variable_slicing.__is_slicing_criterion
obtain_variable_statements = variable_slicing.__obtain_variable_statements
obtain_seed_statements = variable_slicing.__obtain_seed_statements
obtain_slicing_criteria = variable_slicing.__obtain_slicing_criteria
obtain_common_boundary_blocks = variable_slicing.__obtain_common_boundary_blocks
obtain_backward_slice = variable_slicing.__obtain_backward_slice
obtain_complete_computation_slices = variable_slicing.__obtain_complete_computation_slices


class SlicingTestCase(TestCase):

    @staticmethod
    def __get_source_code_0():
        return """
        class A {
            void main() {
                int a = 0;
                int b = 10;
                a = b;
                b += a;
            }
        }
        """

    @staticmethod
    def __get_manager_and_variables_0():
        source_code = SlicingTestCase.__get_source_code_0()
        manager = ProgramGraphsManager(source_code, LANG_JAVA)
        cdg = manager.get_control_dependence_graph()
        function_statements = [statement for statement in cdg.entry_points]
        return manager, obtain_variable_statements(cdg, function_statements[0])

    def test_is_slicing_criterion(self):
        a = Statement(StatementType.ASSIGNMENT, Point(1, 1), Point(1, 2), name="a")
        b = Statement(StatementType.VARIABLE, Point(2, 2), Point(2, 3), name="b")
        c = Statement(StatementType.VARIABLE, Point(3, 3), Point(3, 4), name="a")
        self.assertFalse(is_slicing_criterion(a, a))
        self.assertFalse(is_slicing_criterion(a, b))
        self.assertTrue(is_slicing_criterion(a, c))
        self.assertFalse(is_slicing_criterion(b, a))
        self.assertTrue(is_slicing_criterion(b, b))
        self.assertFalse(is_slicing_criterion(b, c))
        self.assertFalse(is_slicing_criterion(c, a))
        self.assertFalse(is_slicing_criterion(c, b))
        self.assertTrue(is_slicing_criterion(c, c))

    def test_get_complete_computation_slices(self):
        source_code = """
        int n = 0;
        int a = 10;
        int b = 10;
        if (n < 10)
            b = n;
        else
            a = n;
        n = a + b;
        return a;
        """
        slices = variable_slicing.get_complete_computation_slices(
            source_code,
            LANG_JAVA,
            SlicePredicate(lang_to_check_parsing=LANG_JAVA))
        slices = [program_slice for program_slice in slices]
        self.assertEqual(3, len(slices))
        for program_slice in slices:
            if program_slice.variable.name == "a":
                self.assertEqual(
                    "int n = 0;\n"
                    "int a = 10;\n"
                    "int b = 10;\n"
                    "if (n < 10)\n"
                    "    b = n;\n"
                    "else\n"
                    "    a = n;",
                    program_slice.code)
            elif program_slice.variable.name == "b":
                self.assertEqual(
                    "int n = 0;\n"
                    "int b = 10;\n"
                    "if (n < 10)\n"
                    "    b = n;",
                    program_slice.code)
            elif program_slice.variable.name == "n":
                self.assertEqual(
                    "int n = 0;\n"
                    "int a = 10;\n"
                    "int b = 10;\n"
                    "if (n < 10)\n"
                    "    b = n;\n"
                    "else\n"
                    "    a = n;\n"
                    "n = a + b;",
                    program_slice.code)
            else:
                self.assertTrue(False)

    def test_get_complete_computation_slices_goto(self):
        source_code = """
        int a = 10;
        while (1) {
            if (a < 10) {
                a++;
                continue;
            }
            else if (a > 10)
                throw new Exception();
            else
                log.info("!");
            a = 0;
            break;
        }
        return a;
        """
        slices = variable_slicing.get_complete_computation_slices(
            source_code,
            LANG_JAVA,
            SlicePredicate(lang_to_check_parsing=LANG_JAVA))
        for program_slice in slices:
            self.assertEqual(
                "int a = 10;\n"
                "while (1) {\n"
                "    if (a < 10) {\n"
                "        a++;\n"
                "        continue;\n"
                "    }\n"
                "    else if (a > 10)\n"
                "        throw new Exception();\n"
                "    a = 0;\n"
                "    break;\n"
                "}",
                program_slice.code)

    def test_get_complete_computation_slices_try(self):
        source_code = """
        class A {
            int main(String args) {
                char a;
                try {
                    a = args[10];
                }
                catch (Exception e) {
                    e.printStackTrace();
                }
                catch (MyException e) {
                }
                finally {
                    myFoo("a");
                }
            }
        }
        """
        slices = variable_slicing.get_complete_computation_slices(
            source_code,
            LANG_JAVA,
            SlicePredicate(lang_to_check_parsing=LANG_JAVA))
        slices = [program_slice for program_slice in slices]
        self.assertEqual(1, len(slices))
        for program_slice in slices:
            self.assertEqual(
                "char a;\n"
                "try {\n"
                "    a = args[10];\n"
                "}\n"
                "catch (Exception e) {\n"
                "}\n"
                "catch (MyException e) {\n"
                "}\n"
                "finally {\n"
                "    myFoo(\"a\");\n"
                "}",
                program_slice.code)

    def test_get_complete_computation_slices_switch(self):
        source_code = """
        class A {
            int main(String args) {
                int a = 10;
                for (int i = 0; i < 10; i++) {
                    switch(a) {
                        default:
                            a = 1;
                        case 10:
                            myFoo();
                        case 5:
                            break;
                        case 3:
                            continue;
                        case 4:
                            a = -1;
                    }
                }
                return a;
            }
        }
        """
        slices = variable_slicing.get_complete_computation_slices(
            source_code,
            LANG_JAVA)
        slices = [program_slice for program_slice in slices]
        self.assertEqual(2, len(slices))
        for program_slice in slices:
            if program_slice.variable.name == "a":
                self.assertEqual(
                    "int a = 10;\n"
                    "for (int i = 0; i < 10; i++) {\n"
                    "    switch(a) {\n"
                    "        default:\n"
                    "            a = 1;\n"
                    "        case 10:\n"
                    "        case 5:\n"
                    "            break;\n"
                    "        case 3:\n"
                    "            continue;\n"
                    "        case 4:\n"
                    "            a = -1;\n"
                    "    }\n"
                    "}",
                    program_slice.code)
            elif program_slice.variable.name == "i":
                self.assertEqual(
                    "for (int i = 0; i < 10; i++) {\n"
                    "}",
                    program_slice.code)

    def test_get_complete_computation_slices_synchronized(self):
        source_code = """
        class A {
            int main(String args) {
                int a = 0;
                int b = 1;
                synchronized(a) {
                    int c = 10;
                    b = a;
                    c = b;
                }
            }
        }
        """
        slices = variable_slicing.get_complete_computation_slices(
            source_code,
            LANG_JAVA)
        slices = [program_slice for program_slice in slices]
        self.assertEqual(3, len(slices))
        for program_slice in slices:
            if program_slice.variable.name == "a":
                self.assertEqual(
                    "int a = 0;",
                    program_slice.code)
            elif program_slice.variable.name == "b":
                self.assertEqual(
                    "int a = 0;\n"
                    "int b = 1;\n"
                    "synchronized(a) {\n"
                    "    b = a;\n"
                    "}",
                    program_slice.code)
            elif program_slice.variable.name == "c":
                self.assertEqual(
                    "int c = 10;\n"
                    "b = a;\n"
                    "c = b;",
                    program_slice.code)

    def test_get_complete_computation_slices_linear_scopes(self):
        source_code = """
        class A {
            int main(String args) {
                {
                    int b = 1;
                    {
                        {
                            int a = 0;
                        }
                    }
                }
            }
        }
        """
        slices = variable_slicing.get_complete_computation_slices(
            source_code,
            LANG_JAVA)
        slices = [program_slice for program_slice in slices]
        self.assertEqual(2, len(slices))
        for program_slice in slices:
            if program_slice.variable.name == "a":
                self.assertEqual(
                    "int a = 0;",
                    program_slice.code)
            elif program_slice.variable.name == "b":
                self.assertEqual(
                    "int b = 1;",
                    program_slice.code)

    def test_get_complete_computation_slices_double_for(self):
        source_code = """
        class A {
            int main(String args) {
                for (int a = 0; a < n; a++) {
                }
                for (int a = 0; a < n; a++) {
                }
            }
        }
        """
        slices = variable_slicing.get_complete_computation_slices(
            source_code,
            LANG_JAVA)
        slices = [program_slice for program_slice in slices]
        self.assertEqual(2, len(slices))
        for program_slice in slices:
            if program_slice.variable.name == "a":
                self.assertEqual(
                    "for (int a = 0; a < n; a++) {\n"
                    "}",
                    program_slice.code)

    def test_get_complete_computation_slices_unreachable(self):
        source_code = """
        class A {
            int main(String args) {
                int a = 10;
                while (1) {
                    if (a < 10) {
                        a++;
                        continue;
                    }
                    else
                        break;
                    a = 0;
                    break;
                }
                return a;
            }
        }
        """
        slices = variable_slicing.get_complete_computation_slices(
            source_code,
            LANG_JAVA)
        slices = [program_slice for program_slice in slices]
        self.assertEqual(1, len(slices))
        for program_slice in slices:
            self.assertEqual(
                "int a = 10;\n"
                "while (1) {\n"
                "    if (a < 10) {\n"
                "        a++;\n"
                "        continue;\n"
                "    }\n"
                "    else\n"
                "        break;\n"
                "}",
                program_slice.code)

    def test_get_complete_computation_slices_lambda(self):
        source_code = """
        class A {
            public String foo() {
            final String path = "";
            return CompletableFuture.supplyAsync(
                () -> {
                    String p = path;
                    p += "/home";
                    p += "/index.js";
                    return p;
                },
                this.exec);
            }
        }
        """
        slices = variable_slicing.get_complete_computation_slices(
            source_code,
            LANG_JAVA)
        slices = [program_slice for program_slice in slices]
        self.assertEqual(2, len(slices))
        for program_slice in slices:
            if program_slice.variable.name == "path":
                self.assertEqual(
                    "final String path = \"\";",
                    program_slice.code)
            elif program_slice.variable.name == "p":
                self.assertEqual(
                    "String p = path;\n"
                    "p += \"/home\";\n"
                    "p += \"/index.js\";",
                    program_slice.code)

    def test_obtain_variable_statements(self):
        manager, variable_statements = self.__get_manager_and_variables_0()
        self.assertEqual(2, len(variable_statements))
        self.assertEqual({"a", "b"}, {variable_statement.name for variable_statement in variable_statements})

    def test_obtain_seed_statements(self):
        manager, variable_statements = self.__get_manager_and_variables_0()
        for variable_statement in variable_statements:
            seed_statements = obtain_seed_statements(manager, variable_statement)
            self.assertEqual(2, len(seed_statements))
            for seed_statement in seed_statements:
                self.assertEqual(variable_statement.name, seed_statement.name)

    def test_obtain_slicing_criteria(self):
        manager, variable_statements = self.__get_manager_and_variables_0()
        cdg = manager.get_control_dependence_graph()
        function_statements = [statement for statement in cdg.entry_points]
        slicing_criteria = obtain_slicing_criteria(manager, function_statements[0])
        self.assertEqual({"a", "b"}, {key.name for key in slicing_criteria.keys()})
        for variable_statement, seed_statements in slicing_criteria.items():
            self.assertEqual(2, len(seed_statements))
            for seed_statement in seed_statements:
                self.assertEqual(variable_statement.name, seed_statement.name)

    def test_obtain_common_boundary_blocks(self):
        manager, variable_statements = self.__get_manager_and_variables_0()
        for variable_statement in variable_statements:
            seed_statements = obtain_seed_statements(manager, variable_statement)
            self.assertEqual(1, len(obtain_common_boundary_blocks(manager, seed_statements)))

    def test_obtain_backward_slice(self):
        manager, variable_statements = self.__get_manager_and_variables_0()
        cdg = manager.get_control_dependence_graph()
        function_statements = [statement for statement in cdg.entry_points]
        slicing_criteria = obtain_slicing_criteria(manager, function_statements[0])
        basic_blocks = [block for block in manager.get_control_flow_graph()]
        self.assertEqual(1, len(basic_blocks))
        boundary_block = basic_blocks[0]
        for variable_statement, seed_statements in slicing_criteria.items():
            for seed_statement in seed_statements:
                backward_slice = obtain_backward_slice(manager, seed_statement, boundary_block)
                if seed_statement.start_point.line_number == 3:
                    self.assertEqual(
                        {2, 3},
                        {slice_statement.start_point.line_number for slice_statement in backward_slice})
                    self.assertEqual(
                        {3, 7},
                        {slice_statement.end_point.line_number for slice_statement in backward_slice})
                elif seed_statement.start_point.line_number == 4:
                    self.assertEqual(
                        {2, 4},
                        {slice_statement.start_point.line_number for slice_statement in backward_slice})
                    self.assertEqual(
                        {4, 7},
                        {slice_statement.end_point.line_number for slice_statement in backward_slice})
                elif seed_statement.start_point.line_number == 5:
                    self.assertEqual(
                        {2, 3, 4, 5},
                        {slice_statement.start_point.line_number for slice_statement in backward_slice})
                    self.assertEqual(
                        {3, 4, 5, 7},
                        {slice_statement.end_point.line_number for slice_statement in backward_slice})
                elif seed_statement.start_point.line_number == 6:
                    self.assertEqual(
                        {2, 3, 4, 5, 6},
                        {slice_statement.start_point.line_number for slice_statement in backward_slice})
                    self.assertEqual(
                        {3, 4, 5, 6, 7},
                        {slice_statement.end_point.line_number for slice_statement in backward_slice})

    def test_obtain_complete_computation_slices(self):
        manager, variable_statements = self.__get_manager_and_variables_0()
        cdg = manager.get_control_dependence_graph()
        function_statements = [statement for statement in cdg.entry_points]
        slicing_criteria = obtain_slicing_criteria(manager, function_statements[0])
        for variable_statement, seed_statements in slicing_criteria.items():
            complete_computation_slices = obtain_complete_computation_slices(manager, seed_statements)
            self.assertEqual(1, len(complete_computation_slices))

    def test_if_slice_is_continuous_with_block_comments(self) -> None:
        code = """
        int a = 0;
        /* Block slices
           need to be included
        */
        ++a;
        """
        slices = list(get_variable_slices(code, LANG_JAVA))
        self.assertEqual(1, len(slices))
        [program_slice] = slices
        self.assertEqual(1, len(program_slice.ranges_compact))
        [(start, end)] = program_slice.ranges_compact
        self.assertEqual(1, start.line_number)
        self.assertEqual(5, end.line_number)

    def test_if_slice_is_continuous_with_single_comment(self) -> None:
        code = """
        int a = 0;
        // comment
        ++a;
        """
        slices = list(get_variable_slices(code, LANG_JAVA))
        self.assertEqual(1, len(slices))
        [program_slice] = slices
        self.assertEqual(1, len(program_slice.ranges_compact))
        [(start, end)] = program_slice.ranges_compact
        self.assertEqual(1, start.line_number)
        self.assertEqual(3, end.line_number)

    def test_if_slice_is_continuous_with_empty_lines(self) -> None:
        code = """
            int a = 0;

            if (a < 5) {

                --a;
            }
            ++a;
        """
        slices = list(get_variable_slices(code, LANG_JAVA))
        self.assertEqual(1, len(slices))
        [program_slice] = slices
        self.assertEqual(1, len(program_slice.ranges_compact))
        [(start, end)] = program_slice.ranges_compact
        self.assertEqual(start.line_number, 1)
        self.assertEqual(end.line_number, 7)

__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/22'

from unittest import TestCase

from program_slicing.decomposition import variable
from program_slicing.decomposition.slice_predicate import SlicePredicate
from program_slicing.decomposition.variable.slicing import get_variable_slices
from program_slicing.graph.parse import Lang
from program_slicing.graph.statement import Statement, StatementType
from program_slicing.graph.point import Point
from program_slicing.graph.manager import ProgramGraphsManager

is_slicing_criterion = variable.slicing.__is_slicing_criterion
obtain_variable_statements = variable.slicing.__obtain_variable_statements
obtain_seed_statements = variable.slicing.__obtain_seed_statements
obtain_slicing_criteria = variable.slicing.__obtain_slicing_criteria
obtain_common_boundary_blocks = variable.slicing.__obtain_common_boundary_blocks
obtain_backward_slice = variable.slicing.__obtain_backward_slice
obtain_complete_computation_slices = variable.slicing.__obtain_complete_computation_slices


class VariableSlicingTestCase(TestCase):

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
        source_code = VariableSlicingTestCase.__get_source_code_0()
        manager = ProgramGraphsManager(source_code, Lang.JAVA)
        cdg = manager.control_dependence_graph
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

    def test_special_case(self):
        code = """public void bla() {
            int n = 0;
            int a = 10;
            int b = 10;
            if (n < 10)
                b = n;
            else
                a = n;
                n = a + b;
            foo();
            return a;
        }"""
        slices = [s for s in get_variable_slices(
            code,
            Lang.JAVA,
            slice_predicate=SlicePredicate(
                min_amount_of_lines=4,
                min_amount_of_statements=4,
                max_percentage_of_lines=0.8,
                lang_to_check_parsing=Lang.JAVA,
                has_returnable_variable=True,
                cause_code_duplication=False
            ),
            include_noneffective=True
        )]
        self.assertEqual(1, len(slices))

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
        slices = variable.slicing.get_complete_computation_slices(
            source_code,
            Lang.JAVA,
            SlicePredicate(lang_to_check_parsing=Lang.JAVA))
        slices = [program_slice for program_slice in slices]
        self.assertEqual(3, len(slices))
        for program_slice in slices:
            if program_slice.variable.name == "a":
                self.assertEqual(
                    [(Point(1, 8), Point(7, 18))],
                    program_slice.ranges_compact)
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
                self.assertEqual(
                    [(Point(1, 8), Point(1, 18)), (Point(3, 8), Point(5, 18))],
                    program_slice.ranges_compact)
            elif program_slice.variable.name == "n":
                self.assertEqual(
                    [(Point(1, 8), Point(8, 18))],
                    program_slice.ranges_compact)
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
        slices = variable.slicing.get_complete_computation_slices(
            source_code,
            Lang.JAVA,
            SlicePredicate(
                lang_to_check_parsing=Lang.JAVA,
                cause_code_duplication=False
            ))
        slices = [program_slice for program_slice in slices]
        self.assertEqual(1, len(slices))
        for program_slice in slices:
            if program_slice.variable.name == "n":
                self.assertEqual(
                    [(Point(1, 8), Point(8, 18))],
                    program_slice.ranges_compact)
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
        slices = variable.slicing.get_complete_computation_slices(
            source_code,
            Lang.JAVA,
            SlicePredicate(lang_to_check_parsing=Lang.JAVA))
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
            int main() {
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
        slices = variable.slicing.get_complete_computation_slices(
            source_code,
            Lang.JAVA,
            SlicePredicate(lang_to_check_parsing=Lang.JAVA))
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
            int main() {
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
        slices = variable.slicing.get_complete_computation_slices(
            source_code,
            Lang.JAVA)
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
            int main() {
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
        slices = variable.slicing.get_complete_computation_slices(
            source_code,
            Lang.JAVA)
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
            int main() {
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
        slices = variable.slicing.get_complete_computation_slices(
            source_code,
            Lang.JAVA)
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
            int main() {
                for (int a = 0; a < n; a++) {
                }
                for (int a = 0; a < n; a++) {
                }
            }
        }
        """
        slices = variable.slicing.get_complete_computation_slices(
            source_code,
            Lang.JAVA)
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
            int main() {
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
        slices = variable.slicing.get_complete_computation_slices(
            source_code,
            Lang.JAVA)
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
        slices = variable.slicing.get_complete_computation_slices(
            source_code,
            Lang.JAVA)
        slices = [program_slice for program_slice in slices]
        self.assertEqual(1, len(slices))
        for program_slice in slices:
            if program_slice.variable.name == "path":
                self.assertEqual(
                    "final String path = \"\";",
                    program_slice.code)
            # elif program_slice.variable.name == "p":
            #     self.assertEqual(
            #         "String p = path;\n"
            #         "p += \"/home\";\n"
            #         "p += \"/index.js\";",
            #         program_slice.code)

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
        cdg = manager.control_dependence_graph
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
        cdg = manager.control_dependence_graph
        function_statements = [statement for statement in cdg.entry_points]
        slicing_criteria = obtain_slicing_criteria(manager, function_statements[0])
        basic_blocks = [block for block in manager.control_flow_graph]
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
        cdg = manager.control_dependence_graph
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
        slices = list(get_variable_slices(code, Lang.JAVA))
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
        slices = list(get_variable_slices(code, Lang.JAVA))
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
        slices = list(get_variable_slices(code, Lang.JAVA))
        self.assertEqual(1, len(slices))
        [program_slice] = slices
        self.assertEqual(1, len(program_slice.ranges_compact))
        [(start, end)] = program_slice.ranges_compact
        self.assertEqual(1, start.line_number)
        self.assertEqual(7, end.line_number)

    def test_filter(self) -> None:
        code = """
        for (String element : saEquip) {
            String equipName = element.trim();

            // ProtoMech Ammo comes in non-standard amounts.
            int ammoIndex = equipName.indexOf("Ammo (");
            int shotsCount = 0;
            if (ammoIndex > 0) {
                // Try to get the number of shots.
                try {
                    String shots = equipName.substring(ammoIndex + 6, equipName.length() - 1);
                    shotsCount = Integer.parseInt(shots);
                    if (shotsCount < 0) {
                        throw new EntityLoadingException("Invalid number of shots in: " + equipName + ".");
                    }
                } catch (NumberFormatException badShots) {
                    throw new EntityLoadingException("Could not determine the number of shots in: " + equipName + ".");
                }

                // Strip the shots out of the ammo name.
                equipName = equipName.substring(0, ammoIndex + 4);
            }
            EquipmentType etype = EquipmentType.get(equipName);

            if (etype == null) {
                // try w/ prefix
                etype = EquipmentType.get(prefix + equipName);
            }

            if (etype != null) {
                try {
                    // If this is an Ammo slot, only add
                    // the indicated number of shots.
                    if (ammoIndex > 0) {
                        t.addEquipment(etype, nLoc, false, shotsCount);
                    } else {
                        t.addEquipment(etype, nLoc);
                    }
                } catch (LocationFullException ex) {
                    throw new EntityLoadingException(ex.getMessage());
                }
            }
        }"""
        slices = list(get_variable_slices(
            code,
            Lang.JAVA,
            slice_predicate=SlicePredicate(
                min_amount_of_lines=3,
                min_amount_of_statements=2,
                max_amount_of_exit_statements=1,
                cause_code_duplication=False,
                has_returnable_variable=True,
                lang_to_check_parsing=Lang.JAVA
            )
        ))
        self.assertEqual(1, len(slices))
        [program_slice] = slices
        self.assertEqual(1, len(program_slice.ranges_compact))
        [(start, end)] = program_slice.ranges_compact
        self.assertEqual(22, start.line_number)
        self.assertEqual(27, end.line_number)

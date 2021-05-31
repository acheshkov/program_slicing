__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/22'

from unittest import TestCase

from program_slicing.decomposition import slicing
from program_slicing.graph.parse import LANG_JAVA
from program_slicing.graph.statement import Statement, StatementType
from program_slicing.graph.manager import ProgramGraphsManager

is_slicing_criterion = slicing.__is_slicing_criterion
obtain_variable_statements = slicing.__obtain_variable_statements
obtain_seed_statements = slicing.__obtain_seed_statements
obtain_slicing_criteria = slicing.__obtain_slicing_criteria
obtain_common_boundary_blocks = slicing.__obtain_common_boundary_blocks
obtain_backward_slice = slicing.__obtain_backward_slice
obtain_complete_computation_slices = slicing.__obtain_complete_computation_slices


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
        cdg = manager.cdg
        function_statements = [statement for statement in cdg.get_entry_points()]
        return manager, obtain_variable_statements(cdg, function_statements[0])

    def test_decompose_dir(self):
        pass

    def test_decompose_file(self):
        pass

    def test_decompose_code(self):
        source_code = self.__get_source_code_0()
        res = [decomposition for decomposition in slicing.decompose_code(source_code, LANG_JAVA)]
        self.assertEqual(2, len(res))

    def test_is_slicing_criterion(self):
        a = Statement(StatementType.ASSIGNMENT, (1, 1), (1, 2), name="a")
        b = Statement(StatementType.VARIABLE, (2, 2), (2, 3), name="b")
        c = Statement(StatementType.VARIABLE, (3, 3), (3, 4), name="a")
        self.assertFalse(is_slicing_criterion(a, a))
        self.assertFalse(is_slicing_criterion(a, b))
        self.assertTrue(is_slicing_criterion(a, c))
        self.assertFalse(is_slicing_criterion(b, a))
        self.assertTrue(is_slicing_criterion(b, b))
        self.assertFalse(is_slicing_criterion(b, c))
        self.assertFalse(is_slicing_criterion(c, a))
        self.assertFalse(is_slicing_criterion(c, b))
        self.assertTrue(is_slicing_criterion(c, c))

    def test_obtain_variable_statements(self):
        manager, variable_statements = self.__get_manager_and_variables_0()
        self.assertEqual(2, len(variable_statements))
        self.assertEqual({"a", "b"}, {variable_statement.name for variable_statement in variable_statements})

    def test_obtain_seed_statements(self):
        manager, variable_statements = self.__get_manager_and_variables_0()
        cdg = manager.cdg
        function_statements = [statement for statement in cdg.get_entry_points()]
        for variable_statement in variable_statements:
            seed_statements = obtain_seed_statements(cdg, function_statements[0], variable_statement)
            self.assertEqual(2, len(seed_statements))
            for seed_statement in seed_statements:
                self.assertEqual(variable_statement.name, seed_statement.name)

    def test_obtain_slicing_criteria(self):
        manager, variable_statements = self.__get_manager_and_variables_0()
        cdg = manager.cdg
        function_statements = [statement for statement in cdg.get_entry_points()]
        slicing_criteria = obtain_slicing_criteria(cdg, function_statements[0])
        self.assertEqual({"a", "b"}, {key.name for key in slicing_criteria.keys()})
        for variable_statement, seed_statements in slicing_criteria.items():
            self.assertEqual(2, len(seed_statements))
            for seed_statement in seed_statements:
                self.assertEqual(variable_statement.name, seed_statement.name)

    def test_obtain_common_boundary_blocks(self):
        manager, variable_statements = self.__get_manager_and_variables_0()
        cdg = manager.cdg
        function_statements = [statement for statement in cdg.get_entry_points()]
        for variable_statement in variable_statements:
            seed_statements = obtain_seed_statements(cdg, function_statements[0], variable_statement)
            self.assertEqual(1, len(obtain_common_boundary_blocks(manager, seed_statements)))

    def test_obtain_backward_slice(self):
        manager, variable_statements = self.__get_manager_and_variables_0()
        cdg = manager.cdg
        function_statements = [statement for statement in cdg.get_entry_points()]
        slicing_criteria = obtain_slicing_criteria(cdg, function_statements[0])
        basic_blocks = [block for block in manager.cfg]
        self.assertEqual(1, len(basic_blocks))
        boundary_block = basic_blocks[0]
        for variable_statement, seed_statements in slicing_criteria.items():
            for seed_statement in seed_statements:
                backward_slice = obtain_backward_slice(manager, seed_statement, boundary_block)
                if seed_statement.start_point[0] == 3:
                    self.assertEqual(
                        {2, 3},
                        {slice_statement.start_point[0] for slice_statement in backward_slice})
                    self.assertEqual(
                        {3, 7},
                        {slice_statement.end_point[0] for slice_statement in backward_slice})
                elif seed_statement.start_point[0] == 4:
                    self.assertEqual(
                        {2, 4},
                        {slice_statement.start_point[0] for slice_statement in backward_slice})
                    self.assertEqual(
                        {4, 7},
                        {slice_statement.end_point[0] for slice_statement in backward_slice})
                elif seed_statement.start_point[0] == 5:
                    self.assertEqual(
                        {2, 3, 4, 5},
                        {slice_statement.start_point[0] for slice_statement in backward_slice})
                    self.assertEqual(
                        {3, 4, 5, 7},
                        {slice_statement.end_point[0] for slice_statement in backward_slice})
                elif seed_statement.start_point[0] == 6:
                    self.assertEqual(
                        {2, 3, 4, 5, 6},
                        {slice_statement.start_point[0] for slice_statement in backward_slice})
                    self.assertEqual(
                        {3, 4, 5, 6, 7},
                        {slice_statement.end_point[0] for slice_statement in backward_slice})

    def test_obtain_complete_computation_slices(self):
        manager, variable_statements = self.__get_manager_and_variables_0()
        cdg = manager.cdg
        function_statements = [statement for statement in cdg.get_entry_points()]
        slicing_criteria = obtain_slicing_criteria(cdg, function_statements[0])
        for variable_statement, seed_statements in slicing_criteria.items():
            complete_computation_slices = obtain_complete_computation_slices(manager, seed_statements)
            self.assertEqual(1, len(complete_computation_slices))

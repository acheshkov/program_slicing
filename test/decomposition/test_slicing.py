__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/22'

from unittest import TestCase

from program_slicing.decomposition import slicing
from program_slicing.graph.parse import LANG_JAVA
from program_slicing.graph.cdg_node import CDGNode, CDG_NODE_TYPE_VARIABLE, CDG_NODE_TYPE_ASSIGNMENT
from program_slicing.graph.manager import ProgramGraphsManager

is_slicing_criterion = slicing.__is_slicing_criterion
obtain_variable_nodes = slicing.__obtain_variable_nodes
obtain_seed_statement_nodes = slicing.__obtain_seed_statement_nodes
obtain_slicing_criteria = slicing.__obtain_slicing_criteria


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
    def __get_cdg_and_variables_0():
        source_code = SlicingTestCase.__get_source_code_0()
        manager = ProgramGraphsManager(source_code, LANG_JAVA)
        cdg = manager.cdg
        function_nodes = [node for node in cdg.get_entry_points()]
        return cdg, obtain_variable_nodes(cdg, function_nodes[0])

    def test_decompose_dir(self):
        pass

    def test_decompose_file(self):
        pass

    def test_decompose_code(self):
        source_code = self.__get_source_code_0()
        res = [decomposition for decomposition in slicing.decompose_code(source_code, LANG_JAVA)]
        self.assertEqual(2, len(res))

    def test_is_slicing_criterion(self):
        a = CDGNode("", CDG_NODE_TYPE_ASSIGNMENT, (1, 1), (1, 2), name="a")
        b = CDGNode("", CDG_NODE_TYPE_VARIABLE, (2, 2), (2, 3), name="b")
        c = CDGNode("", CDG_NODE_TYPE_VARIABLE, (3, 3), (3, 4), name="a")
        self.assertFalse(is_slicing_criterion(a, a))
        self.assertFalse(is_slicing_criterion(a, b))
        self.assertTrue(is_slicing_criterion(a, c))
        self.assertFalse(is_slicing_criterion(b, a))
        self.assertFalse(is_slicing_criterion(b, b))
        self.assertFalse(is_slicing_criterion(b, c))
        self.assertFalse(is_slicing_criterion(c, a))
        self.assertFalse(is_slicing_criterion(c, b))
        self.assertFalse(is_slicing_criterion(c, c))

    def test_obtain_variable_nodes(self):
        cdg, variable_nodes = self.__get_cdg_and_variables_0()
        self.assertEqual(2, len(variable_nodes))
        self.assertEqual({"a", "b"}, {variable_node.name for variable_node in variable_nodes})

    def test_obtain_seed_statement_nodes(self):
        cdg, variable_nodes = self.__get_cdg_and_variables_0()
        function_nodes = [node for node in cdg.get_entry_points()]
        for variable_node in variable_nodes:
            seed_statement_nodes = obtain_seed_statement_nodes(cdg, function_nodes[0], variable_node)
            self.assertEqual(1, len(seed_statement_nodes))
            for seed_statement_node in seed_statement_nodes:
                self.assertEqual(variable_node.name, seed_statement_node.name)

    def test_obtain_slicing_criteria(self):
        cdg, variable_nodes = self.__get_cdg_and_variables_0()
        function_nodes = [node for node in cdg.get_entry_points()]
        slicing_criteria = obtain_slicing_criteria(cdg, function_nodes[0])
        self.assertEqual({"a", "b"}, {key.name for key in slicing_criteria.keys()})
        for variable_node, seed_statement_nodes in slicing_criteria.items():
            self.assertEqual(1, len(seed_statement_nodes))
            for seed_statement_node in seed_statement_nodes:
                self.assertEqual(variable_node.name, seed_statement_node.name)

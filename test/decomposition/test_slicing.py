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
        return "class A {" \
               "    void main() {" \
               "        int a = 0;" \
               "        int b = 10;" \
               "        a = b;" \
               "        b += a;" \
               "    }" \
               "}"

    def test_decompose_dir(self):
        pass

    def test_decompose_file(self):
        pass

    def test_decompose_code(self):
        source_code = self.__get_source_code_0()
        res = [decomposition for decomposition in slicing.decompose_code(source_code, LANG_JAVA)]
        self.assertEqual(2, len(res))

    def test_is_slicing_criterion(self):
        a = CDGNode("", CDG_NODE_TYPE_ASSIGNMENT, (1, 1), name="a")
        b = CDGNode("", CDG_NODE_TYPE_VARIABLE, (2, 2), name="b")
        c = CDGNode("", CDG_NODE_TYPE_VARIABLE, (3, 3), name="a")
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
        source_code = self.__get_source_code_0()
        manager = ProgramGraphsManager(source_code, LANG_JAVA)
        cdg = manager.cdg
        function_nodes = cdg.get_entry_points()
        self.assertEqual(1, len(function_nodes))
        variable_nodes = obtain_variable_nodes(cdg, function_nodes.pop())
        self.assertEqual(2, len(variable_nodes))
        self.assertEqual({"a", "b"}, {variable_node.name for variable_node in variable_nodes})

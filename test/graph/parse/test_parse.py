__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/30'

from unittest import TestCase

from program_slicing.graph.parse import \
    control_flow_graph, \
    control_dependence_graph, \
    data_dependence_graph, \
    program_dependence_graph, \
    LANG_JAVA


class ParseTestCase(TestCase):

    def __check_graph(self, graph) -> None:
        self.assertIsNotNone(graph)
        self.assertTrue(len(graph) > 0)

    def test_control_flow_graph(self) -> None:
        code = "class A { void foo() {} }"
        self.__check_graph(control_flow_graph(code, LANG_JAVA))

    def test_control_dependence_graph(self) -> None:
        code = "class A { void foo() {} }"
        self.__check_graph(control_dependence_graph(code, LANG_JAVA))

    def test_data_dependence_graph(self) -> None:
        code = "class A { void foo() {} }"
        self.__check_graph(data_dependence_graph(code, LANG_JAVA))

    def test_program_dependence_graph(self) -> None:
        code = "class A { void foo() {} }"
        self.__check_graph(program_dependence_graph(code, LANG_JAVA))

__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/30'

from unittest import TestCase

from program_slicing.graph.parse import \
    control_flow_graph, \
    control_dependence_graph, \
    LANG_JAVA


class ParseTestCase(TestCase):

    def check_graph(self, graph):
        self.assertIsNotNone(graph)
        # TODO: add more checks

    def test_control_flow_graph(self):
        lang = LANG_JAVA
        code = "class A {}"
        self.check_graph(control_flow_graph(code, lang))

    def test_control_dependence_graph(self):
        lang = LANG_JAVA
        code = "class A {}"
        self.check_graph(control_dependence_graph(code, lang))

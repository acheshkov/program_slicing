__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/30'

from unittest import TestCase
from program_slicing.parse.parse import \
    control_graph, \
    control_flow_graph, \
    control_dependency_graph, \
    FILE_EXT_JAVA


class ParseTestCase(TestCase):

    def check_cg(self, cg):
        self.assertIsNotNone(cg)
        self.assertIsNotNone(cg.root)
        self.assertIsNotNone(cg.root.children)
        self.assertTrue(len(cg.root.children) > 0)

    def test_control_graph(self):
        ext = FILE_EXT_JAVA
        code = "class A {}"
        self.check_cg(control_graph(code, ext))

    def test_control_flow_graph(self):
        ext = FILE_EXT_JAVA
        code = "class A {}"
        self.check_cg(control_flow_graph(code, ext))

    def test_control_dependency_graph(self):
        ext = FILE_EXT_JAVA
        code = "class A {}"
        self.check_cg(control_dependency_graph(code, ext))

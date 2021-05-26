__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/05/24'

from unittest import TestCase

from program_slicing.decomposition.code_lines_slicer import CodeLinesSlicer, RangeType
from program_slicing.graph.statement import Statement, StatementType


class CodeLinesSlicerTestCase(TestCase):

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
    def __get_code_lines_slicer_0():
        code_lines_slicer = CodeLinesSlicer(CodeLinesSlicerTestCase.__get_source_code_0().split("\n"))
        function_body = Statement(StatementType.statements, (2, 24), (7, 13))
        variable_a = Statement(StatementType.variable, (3, 16), (3, 26))
        variable_b = Statement(StatementType.variable, (4, 16), (4, 27))
        code_lines_slicer.add_statement(function_body)
        code_lines_slicer.add_statement(variable_a)
        code_lines_slicer.add_statement(variable_b)
        code_lines_slicer.add_range((5, 16), (5, 22), RangeType.FULL)
        return code_lines_slicer

    def test_get_ranges(self):
        program_slice = CodeLinesSlicerTestCase.__get_code_lines_slicer_0()
        self.assertEqual([
            ((2, 24), (2, 25)),
            ((3, 12), (3, 26)),
            ((4, 12), (4, 27)),
            ((5, 12), (5, 22)),
            ((7, 12), (7, 13))], program_slice.get_ranges())

    def test_get_slice(self):
        program_slice = CodeLinesSlicerTestCase.__get_code_lines_slicer_0()
        self.assertEqual(
            "{\n"
            "    int a = 0;\n"
            "    int b = 10;\n"
            "    a = b;\n"
            "}",
            program_slice.get_slice_code())

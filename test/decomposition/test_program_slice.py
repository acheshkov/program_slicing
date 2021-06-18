__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/05/24'

from unittest import TestCase

from program_slicing.decomposition.program_slice import ProgramSlice, RangeType
from program_slicing.graph.statement import Statement, StatementType


class ProgramSliceTestCase(TestCase):

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
    def __get_program_slice_0():
        program_slice = ProgramSlice(ProgramSliceTestCase.__get_source_code_0().split("\n"))
        function_body = Statement(StatementType.SCOPE, (2, 24), (7, 13))
        variable_a = Statement(StatementType.VARIABLE, (3, 16), (3, 26))
        variable_b = Statement(StatementType.VARIABLE, (4, 16), (4, 27))
        program_slice.add_statement(function_body)
        program_slice.add_statement(variable_a)
        program_slice.add_statement(variable_b)
        program_slice.add_range((5, 16), (5, 22), RangeType.FULL)
        return program_slice

    @staticmethod
    def __get_source_code_1():
        return """
        class A {
            void main() {
                String s = "line1" +
"line2" +
                    "line3" +
"very very very long line4";
            }
        }
        """

    @staticmethod
    def __get_program_slice_1():
        program_slice = ProgramSlice(ProgramSliceTestCase.__get_source_code_1().split("\n"))
        function_body = Statement(StatementType.SCOPE, (2, 24), (7, 13))
        variable_s = Statement(StatementType.UNKNOWN, (3, 16), (6, 28))
        program_slice.add_statement(function_body)
        program_slice.add_statement(variable_s)
        return program_slice

    def test_get_ranges(self):
        program_slice = ProgramSliceTestCase.__get_program_slice_0()
        self.assertEqual([
            ((3, 16), (3, 26)),
            ((4, 16), (4, 27)),
            ((5, 16), (5, 22))], program_slice.ranges)
        program_slice = ProgramSliceTestCase.__get_program_slice_1()
        self.assertEqual([
            ((3, 16), (3, 36)),
            ((4, 0), (4, 9)),
            ((5, 16), (5, 29)),
            ((6, 0), (6, 28))], program_slice.ranges)

    def test_get_slice(self):
        program_slice = ProgramSliceTestCase.__get_program_slice_0()
        self.assertEqual(
            "int a = 0;\n"
            "int b = 10;\n"
            "a = b;"
            ,
            program_slice.code)
        program_slice = ProgramSliceTestCase.__get_program_slice_1()
        self.assertEqual(
            "String s = \"line1\" +\n"
            "\"line2\" +\n"
            "    \"line3\" +\n"
            "\"very very very long line4\";"
            ,
            program_slice.code)

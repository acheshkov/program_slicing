__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/06/07'

from unittest import TestCase
from typing import List, Tuple

from program_slicing.graph.manager import ProgramGraphsManager
from program_slicing.graph.statement import Statement, StatementType
from program_slicing.graph.point import Point
from program_slicing.decomposition.program_slice import ProgramSlice
from program_slicing.decomposition import check_slice
from program_slicing.graph.parse import parse


class CheckSliceTestCase(TestCase):

    @staticmethod
    def __get_ranges_0() -> List[Tuple[Point, Point]]:
        return [
            (Point(1, 0), Point(1, 18)),
            (Point(2, 0), Point(5, 14)),
            (Point(7, 0), Point(7, 14)),
            (Point(3, 0), Point(3, 14))
        ]

    @staticmethod
    def __get_statements_0() -> List[Statement]:
        return [Statement(
            StatementType.UNKNOWN,
            ranges[0],
            ranges[1]) for ranges in CheckSliceTestCase.__get_ranges_0()
        ]

    @staticmethod
    def __get_slice_0() -> ProgramSlice:
        program_slice = ProgramSlice("""
        int a = 0;
        int b = 0;
        int c = 0;
        a = b;
        a = c;
        b = a;
        b = c;
        c = a;
        c = b;
        """.split("\n"))
        for statement in CheckSliceTestCase.__get_statements_0():
            program_slice.add_statement(statement)
        return program_slice

    @staticmethod
    def __get_slice_1() -> ProgramSlice:
        source_lines = """int n = 10;
        hook:
        for(int i = 0; i < n; i++) {
            i++;
            break hook;
        }
        """.split("\n")
        program_slice = ProgramSlice(source_lines).from_ranges([
            (Point(0, 0), Point(len(source_lines) - 1, len(source_lines[-1])))
        ])
        program_slice.variable = Statement(StatementType.VARIABLE, Point(2, 16), Point(2, 21), name="i")
        return program_slice

    @staticmethod
    def __get_slice_2() -> ProgramSlice:
        source_lines = """
        for(int i = 0; i < n; i++) {
            break hook;
        }
        """.split("\n")
        return ProgramSlice(source_lines).from_ranges([
            (Point(0, 0), Point(len(source_lines) - 1, len(source_lines[-1])))
        ])

    def test_statements(self) -> None:
        self.assertTrue(
            check_slice(
                CheckSliceTestCase.__get_slice_0(),
                min_amount_of_lines=6,
                max_amount_of_lines=6))
        self.assertFalse(
            check_slice(
                CheckSliceTestCase.__get_slice_0(),
                min_amount_of_lines=7,
                max_amount_of_lines=7))
        self.assertFalse(
            check_slice(
                CheckSliceTestCase.__get_slice_0(),
                min_amount_of_lines=5,
                max_amount_of_lines=5))
        self.assertTrue(
            check_slice(
                CheckSliceTestCase.__get_slice_0(),
                lang_to_check_parsing=parse.Lang.JAVA,
                min_amount_of_statements=6,
                max_amount_of_statements=6))
        self.assertFalse(
            check_slice(
                CheckSliceTestCase.__get_slice_0(),
                lang_to_check_parsing=parse.Lang.JAVA,
                min_amount_of_statements=7,
                max_amount_of_statements=7))
        self.assertFalse(
            check_slice(
                CheckSliceTestCase.__get_slice_0(),
                lang_to_check_parsing=parse.Lang.JAVA,
                min_amount_of_statements=5,
                max_amount_of_statements=5))

    def test_parsing(self) -> None:
        self.assertTrue(
            check_slice(
                CheckSliceTestCase.__get_slice_1(),
                lang_to_check_parsing=parse.Lang.JAVA
            )
        )
        self.assertFalse(
            check_slice(
                CheckSliceTestCase.__get_slice_2(),
                lang_to_check_parsing=parse.Lang.JAVA
            )
        )

    def test_returnable_variable(self) -> None:
        self.assertFalse(
            check_slice(
                CheckSliceTestCase.__get_slice_1(),
                lang_to_check_parsing=parse.Lang.JAVA,
                has_returnable_variable=True
            )
        )

    def test_context(self) -> None:
        code = """
        int a = 0;
        int b = 0;
        while(a < 10) {
            if foo(a + b) {
                return 0;
            }
            if (a > 10) {
                throw new Exception();
            }
        }
        """
        manager = ProgramGraphsManager(code, parse.Lang.JAVA)
        program_slice = ProgramSlice(code.split("\n"), context=manager).from_ranges(
            [
                (Point(1, 8), Point(1, 18)),
                (Point(3, 8), Point(6, 13)),
                (Point(10, 8), Point(10, 9))
            ]
        )
        self.assertFalse(
            check_slice(
                program_slice,
                min_amount_of_exit_statements=1,
                max_amount_of_exit_statements=1,
                context=manager))
        self.assertTrue(
            check_slice(
                program_slice,
                min_amount_of_exit_statements=2,
                max_amount_of_exit_statements=2,
                context=manager))
        self.assertFalse(
            check_slice(
                program_slice,
                min_amount_of_exit_statements=3,
                max_amount_of_exit_statements=3,
                context=manager))

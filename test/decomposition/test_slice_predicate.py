__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/06/07'

from unittest import TestCase
from typing import List, Tuple

from program_slicing.graph.statement import Statement, StatementType, StatementLineNumber, StatementColumnNumber
from program_slicing.decomposition.program_slice import ProgramSlice
from program_slicing.decomposition import check_slice


class CheckSliceTestCase(TestCase):

    @staticmethod
    def __get_ranges_0() -> List[Tuple[
            Tuple[StatementLineNumber, StatementColumnNumber],
            Tuple[StatementLineNumber, StatementColumnNumber]]]:
        return [
            ((1, 0), (1, 2)),
            ((2, 0), (5, 1)),
            ((7, 0), (7, 2)),
            ((3, 0), (3, 2))
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
        slicer = ProgramSlice("""
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
            slicer.add_statement(statement)
        return slicer

    def test_statements(self):
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

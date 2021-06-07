__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/06/07'

from unittest import TestCase
from typing import List, Tuple

from program_slicing import utils
from program_slicing.graph.statement import Statement, StatementType, StatementLineNumber, StatementColumnNumber
from program_slicing.decomposition.code_lines_slicer import CodeLinesSlicer


class FilterSlicesTestCase(TestCase):

    @staticmethod
    def __get_ranges_list_0() -> List[List[Tuple[
            Tuple[StatementLineNumber, StatementColumnNumber],
            Tuple[StatementLineNumber, StatementColumnNumber]]]]:
        return [
            [
                ((1, 0), (1, 2)),
                ((2, 0), (5, 1)),
                ((7, 0), (7, 2)),
                ((3, 0), (3, 2))
            ],
            [
                ((1, 0), (1, 2)),
                ((2, 0), (5, 1)),
                ((7, 0), (7, 2)),
                ((3, 0), (3, 2)),
                ((8, 0), (8, 1))
            ],
            [
                ((1, 0), (1, 2)),
                ((2, 0), (5, 1)),
                ((3, 0), (3, 2))
            ],
        ]

    @staticmethod
    def __get_statements__list_0() -> List[List[Statement]]:
        return [
            [
                Statement(
                    StatementType.UNKNOWN,
                    ranges[0],
                    ranges[1]) for ranges in ranges_list
            ] for ranges_list in FilterSlicesTestCase.__get_ranges_list_0()
        ]

    @staticmethod
    def __get_slicers_0() -> List[CodeLinesSlicer]:
        code = """
        int a = 0;
        int b = 0;
        int c = 0;
        a = b;
        a = c;
        b = a;
        b = c;
        c = a;
        c = b;
        """.split("\n")
        slicers = []
        for statement_list in FilterSlicesTestCase.__get_statements__list_0():
            slicer = CodeLinesSlicer(code)
            for statement in statement_list:
                slicer.add_statement(statement)
            slicers.append(slicer)
        return slicers

    def test_ranges_list(self):
        ranges_0 = FilterSlicesTestCase.__get_ranges_list_0()
        self.assertEqual(
            [ranges_0[0]],
            [item for item in utils.filter_slices(ranges_0).by_min_amount_of_lines(6).by_max_amount_of_lines(6)])
        self.assertEqual(
            [ranges_0[1]],
            [item for item in utils.filter_slices(ranges_0).by_min_amount_of_lines(7).by_max_amount_of_lines(7)])
        self.assertEqual(
            [ranges_0[2]],
            [item for item in utils.filter_slices(ranges_0).by_min_amount_of_lines(5).by_max_amount_of_lines(5)])

    def test_statements_list(self):
        statements_0 = FilterSlicesTestCase.__get_statements__list_0()
        self.assertEqual(
            [statements_0[0]],
            [item for item in utils.filter_slices(statements_0).by_min_amount_of_lines(6).by_max_amount_of_lines(6)])
        self.assertEqual(
            [statements_0[1]],
            [item for item in utils.filter_slices(statements_0).by_min_amount_of_lines(7).by_max_amount_of_lines(7)])
        self.assertEqual(
            [statements_0[2]],
            [item for item in utils.filter_slices(statements_0).by_min_amount_of_lines(5).by_max_amount_of_lines(5)])

    def test_slicers(self):
        slicers_0 = FilterSlicesTestCase.__get_slicers_0()
        self.assertEqual(
            [slicers_0[0]],
            [item for item in utils.filter_slices(slicers_0).by_min_amount_of_lines(6).by_max_amount_of_lines(6)])
        self.assertEqual(
            [slicers_0[1]],
            [item for item in utils.filter_slices(slicers_0).by_min_amount_of_lines(7).by_max_amount_of_lines(7)])
        self.assertEqual(
            [slicers_0[2]],
            [item for item in utils.filter_slices(slicers_0).by_min_amount_of_lines(5).by_max_amount_of_lines(5)])

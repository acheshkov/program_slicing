__licence__ = 'MIT'
__author__ = 'KatGarmash'
__credits__ = ['KatGarmash']
__maintainer__ = 'KatGarmash'
__date__ = '2021/10/21'


import unittest

import numpy as np

from program_slicing.decomposition.block.extension.scoring import length_score_hh, nesting_depth_score_hh, \
    nesting_area_score_hh, parameters_score_hh, aggregate_score_hh
from program_slicing.decomposition.program_slice import ProgramSlice
from program_slicing.graph.manager import ProgramGraphsManager
from program_slicing.graph.parse import Lang
from program_slicing.graph.point import Point


class SliceScoringTestCase(unittest.TestCase):

    def test_all_scoring_functions(self) -> None:
        code = """
        public void methodEx() {
            while (cond()) {
                int i = 1;
                if (cond2(i)) {
                    do1(i);
                }
            }
        }
        """
        manager = ProgramGraphsManager(code, Lang.JAVA)
        slice_statements = manager.get_statements_in_range(Point(4, 0), Point(6, 10000))
        extraction = ProgramSlice(code.split("\n"), context=manager).from_statements(slice_statements)
        length_score = length_score_hh(code.split("\n")[1:], extraction)
        self.assertEqual(0.3, np.around(length_score, decimals=1))
        method_statements = None
        statement_dic = None
        depth_score = nesting_depth_score_hh(extraction, statement_dic, method_statements)
        self.assertEqual(1, depth_score)
        area_score = nesting_area_score_hh(extraction, statement_dic, method_statements)
        self.assertEqual(2, area_score)
        parameters_score = parameters_score_hh(extraction)
        self.assertEqual(3, parameters_score)
        aggregate_score = aggregate_score_hh(code, extraction)
        self.assertEqual(6.3, aggregate_score)
        # TODO: silva

    def test_all_scoring_functions_double_loop(self) -> None:
        code = """
        public void methodEx() {
            while (cond()) {
                int i = 1;
                if (cond2(i)) {
                    do1(i);
                }
            }
            for (int j = 1; j < 10 ; j++) {
                do2();
                do3();
            }
        }
        """
        manager = ProgramGraphsManager(code, Lang.JAVA)
        slice_statements = manager.get_statements_in_range(Point(8, 0), Point(11, 10000))
        extraction = ProgramSlice(code.split("\n"), context=manager).from_statements(slice_statements)
        length_score = length_score_hh(code.split("\n")[1:], extraction)
        self.assertEqual(0.4, np.around(length_score, decimals=1))
        method_statements = None
        statement_dic = None
        depth_score = nesting_depth_score_hh(extraction, statement_dic, method_statements)
        self.assertEqual(0, depth_score)
        area_score = nesting_area_score_hh(extraction, statement_dic, method_statements)
        self.assertEqual(4 / 3, area_score)
        parameters_score = parameters_score_hh(extraction)
        self.assertEqual(4, parameters_score)
        aggregate_score = aggregate_score_hh(code, extraction)
        self.assertEqual(4.4 + 4 / 3, aggregate_score)
        # TODO: silva

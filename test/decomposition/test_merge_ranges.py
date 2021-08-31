from unittest import TestCase
from program_slicing.decomposition.merge_range import merge_ranges
from program_slicing.graph.point import Point


class TestMergeRanges(TestCase):

    def test_merge_ranges_emty_slice(self):
        slice_ranges = [
        ]
        stmt_lines = [1, 2, 3]
        ranges = merge_ranges(stmt_lines, slice_ranges)
        self.assertEqual(len(ranges), 0)

    def test_merge_ranges_single(self):
        slice_ranges = [
            (Point(1, 0), Point(1, 0)),
            (Point(3, 0), Point(3, 0)),
        ]
        stmt_lines = [1, 3, 4]
        ranges = merge_ranges(stmt_lines, slice_ranges)
        self.assertEqual(len(ranges), 1)
        self.assertEqual(ranges[0][0].line_number, 1)
        self.assertEqual(ranges[0][1].line_number, 3)

    def test_merge_ranges_single_continious(self):
        slice_ranges = [
            (Point(1, 0), Point(1, 0)),
            (Point(2, 0), Point(2, 0)),
            (Point(3, 0), Point(3, 0))
        ]
        stmt_lines = [1, 2, 3]
        ranges = merge_ranges(stmt_lines, slice_ranges)
        self.assertEqual(len(ranges), 1)
        self.assertEqual(ranges[0][0].line_number, 1)
        self.assertEqual(ranges[0][1].line_number, 3)

    def test_merge_ranges_two_continious(self):
        slice_ranges = [
            (Point(1, 0), Point(1, 0)),
            (Point(2, 0), Point(2, 0)),
            (Point(3, 0), Point(3, 0)),
            (Point(5, 0), Point(5, 0)),
            (Point(6, 0), Point(6, 0)),
            (Point(7, 0), Point(7, 0))
        ]
        stmt_lines = [1, 2, 3, 4, 5, 6, 7]
        ranges = merge_ranges(stmt_lines, slice_ranges)
        self.assertEqual(len(ranges), 2)
        range_1 = ranges[0]
        range_2 = ranges[1]
        self.assertEqual(range_1[0].line_number, 1)
        self.assertEqual(range_1[1].line_number, 3)
        self.assertEqual(range_2[0].line_number, 5)
        self.assertEqual(range_2[1].line_number, 7)

    def test_merge_ranges_single_non_continious(self):
        slice_ranges = [
            (Point(1, 0), Point(1, 0)),
            (Point(3, 0), Point(3, 0))
        ]
        stmt_lines = [1, 2, 3]
        ranges = merge_ranges(stmt_lines, slice_ranges)
        self.assertEqual(len(ranges), 2)
        self.assertEqual(ranges[0][0].line_number, 1)
        self.assertEqual(ranges[1][0].line_number, 3)

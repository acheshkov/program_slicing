# from program_slicing.decomposition.program_slice import ProgramSlice
from program_slicing.graph.point import Point
from typing import List, Tuple, Set
from functools import reduce

Range = Tuple[Point, Point]
EmptyLinesAndComments = Set[int]


def merge_ranges(stmt_lines: List[int], ranges: List[Range]) -> List[Range]:
    '''
        Takes list of lines numbers with statments and list of line ranges.
        Returns a new list of ranges where ranges are merged if there are no line with statements
        between them
    '''
    all_non_stmt = set(range(min(stmt_lines), max(stmt_lines) + 1)) - set(stmt_lines)
    ranges = sorted(ranges, key=lambda r: r[0].line_number)
    return reduce(merge, ranges, ([], all_non_stmt))[0]


def merge(accum: Tuple[List[Range], EmptyLinesAndComments], r: Range) -> Tuple[List[Range], EmptyLinesAndComments]:
    rs, lines = accum
    if len(rs) == 0:
        return [r], lines
    if can_be_merged(rs[-1], r, lines):
        rs[-1] = (Point(rs[-1][0].line_number, rs[-1][0].column_number), Point(r[1].line_number, r[1].column_number))
    else:
        rs.append(r)
    return rs, lines


def can_be_merged(r1: Range, r2: Range, lines: EmptyLinesAndComments) -> bool:
    _, fst_point_end = r1
    snd_point_start, _ = r2
    assert fst_point_end.line_number <= snd_point_start.line_number
    if snd_point_start.line_number - fst_point_end.line_number <= 1:
        return True

    lines_between_ranges = set(range(fst_point_end.line_number + 1, snd_point_start.line_number))

    if len(lines_between_ranges & lines) == len(lines_between_ranges):
        return True

    return False

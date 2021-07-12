__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/04/20'

import bisect
from typing import Dict, Set, List, Tuple, Optional

import networkx

from program_slicing.graph.statement import Statement, StatementType
from program_slicing.graph.point import Point


class DataDependenceGraph(networkx.DiGraph):

    def __init__(self) -> None:
        super().__init__()
        self.__entry_points: Set[Statement] = set()

    @property
    def entry_points(self) -> Set[Statement]:
        return self.__entry_points

    def add_entry_point(self, root: Statement) -> None:
        self.__entry_points.add(root)

    def build_scope_statement_dictionary(self) -> Dict[Statement, Statement]:
        scopes_for_start_point: Dict[Point, Statement] = {}
        scopes_for_end_point: Dict[Point, Statement] = {}
        scopes: List[Statement] = sorted([
            statement for statement in self if
            statement.statement_type == StatementType.SCOPE or
            statement.statement_type == StatementType.GOTO or
            statement.statement_type == StatementType.BRANCH or
            statement.statement_type == StatementType.LOOP or
            statement.statement_type == StatementType.FUNCTION
        ], key=lambda statement: (
            statement.start_point,
            (-statement.end_point.line_number, -statement.end_point.column_number)
        ))
        points = []
        for scope in scopes:
            interval_start, interval_end = DataDependenceGraph.__obtain_interval(points, scope)
            if interval_start != scope.start_point:
                bisect.insort(points, scope.start_point)
                # insort is slow on array list, use linked list instead
                if interval_start in scopes_for_start_point:
                    scopes_for_end_point[scope.start_point] = scopes_for_start_point[interval_start]
            if interval_end != scope.end_point:
                bisect.insort(points, scope.end_point)
                # insort is slow on array list, use linked list instead
                if interval_end in scopes_for_end_point:
                    scopes_for_start_point[scope.end_point] = scopes_for_end_point[interval_end]
            scopes_for_start_point[scope.start_point] = scope
            scopes_for_end_point[scope.end_point] = scope
        result = {}
        for statement in self:
            interval_start, interval_end = self.__obtain_interval(points, statement)
            scope = None if (interval_start is None or interval_end is None) else \
                scopes_for_start_point.get(interval_start, None)
            if scope is not None:
                result[statement] = scope
        return result

    @staticmethod
    def __obtain_interval(points: List[Point], statement: Statement) -> Tuple[Optional[Point], Optional[Point]]:
        nearest_start_point_id = bisect.bisect_right(points, statement.start_point) - 1
        nearest_start_point = None if nearest_start_point_id < 0 else points[nearest_start_point_id]
        nearest_end_point_id = bisect.bisect_left(points, statement.start_point)
        nearest_end_point = None if nearest_end_point_id >= len(points) else points[nearest_end_point_id]
        return nearest_start_point, nearest_end_point

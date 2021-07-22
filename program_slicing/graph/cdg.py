__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/30'

import bisect
from typing import Set, Dict, List, Tuple, Optional

import networkx

from program_slicing.graph.statement import Statement, StatementType
from program_slicing.graph.point import Point


class ControlDependenceGraph(networkx.DiGraph):

    def __init__(self) -> None:
        super().__init__()
        self.__entry_points: Set[Statement] = set()
        self.__control_flow: Dict[Statement, List[Statement]] = {}
        self.__scope_dependency: Dict[Statement, Statement] = {}

    @property
    def entry_points(self) -> Set[Statement]:
        return self.__entry_points

    @property
    def control_flow(self) -> Dict[Statement, List[Statement]]:
        return self.__control_flow

    @property
    def scope_dependency(self) -> Dict[Statement, Statement]:
        return self.__scope_dependency

    def add_entry_point(self, root: Statement) -> None:
        self.__entry_points.add(root)

    def set_scope_dependency(self, scope_dependency: Dict[Statement, Statement]) -> None:
        self.__scope_dependency = scope_dependency

    def build_scope_dependency(self) -> None:
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
        scope_container = {}
        for scope in scopes:
            interval_start, interval_end = ControlDependenceGraph.__obtain_interval(points, scope)
            scope_containing_scope = None if (interval_start is None or interval_end is None) else \
                scopes_for_start_point.get(interval_start, None)
            if scope_containing_scope is not None:
                scope_container[scope] = scope_containing_scope
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
        self.__fill_scope_dependency(points, scopes_for_start_point, scopes_for_end_point, scope_container)

    def __fill_scope_dependency(
            self,
            points: List[Point],
            scopes_for_start_point: Dict[Point, Statement],
            scopes_for_end_point: Dict[Point, Statement],
            scope_container: Dict[Statement, Statement]):
        for statement in self:
            interval_start, interval_end = self.__obtain_interval(points, statement)
            scope = None
            if interval_start is not None and interval_end is not None:
                start_point_scope = scopes_for_start_point.get(interval_start, None)
                end_point_scope = scopes_for_end_point.get(interval_end, None)
                if start_point_scope is None or end_point_scope is None:
                    scope = None
                elif start_point_scope == end_point_scope or \
                        start_point_scope.start_point <= end_point_scope.start_point and \
                        start_point_scope.end_point >= end_point_scope.end_point:
                    scope = start_point_scope
                else:
                    scope = end_point_scope
            if scope == statement:
                scope = scope_container.get(scope, None)
            if scope is not None:
                self.__scope_dependency[statement] = scope

    @staticmethod
    def __obtain_interval(points: List[Point], statement: Statement) -> Tuple[Optional[Point], Optional[Point]]:
        nearest_start_point_id = bisect.bisect_right(points, statement.start_point) - 1
        nearest_start_point = None if nearest_start_point_id < 0 else points[nearest_start_point_id]
        nearest_end_point_id = bisect.bisect_left(points, statement.end_point)
        nearest_end_point = None if nearest_end_point_id >= len(points) else points[nearest_end_point_id]
        return nearest_start_point, nearest_end_point

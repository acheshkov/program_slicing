__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/30'

from unittest import TestCase

from program_slicing.graph.statement import Statement, StatementType
from program_slicing.graph.point import Point


class StatementTestCase(TestCase):

    def test_repr_full(self) -> None:
        statement = Statement(
            StatementType.ASSIGNMENT,
            Point(10, 20),
            Point(10, 31),
            {"args"},
            "my_variable",
            "assignment_expression")
        self.assertEqual(
            "ASSIGNMENT(assignment_expression) 'my_variable' affected by variables {'args'} "
            "position in code: (10, 20) - (10, 31)", str(statement))
        self.assertEqual(
            "Statement("
            "statement_type=StatementType.ASSIGNMENT, "
            "ast_node_type=assignment_expression, "
            "name='my_variable', "
            "affected_by={'args'}, "
            "start_point=(10, 20), "
            "end_point=(10, 31))", repr(statement))

    def test_repr_short(self) -> None:
        statement = Statement(
            StatementType.GOTO,
            Point(10, 20),
            Point(10, 24),
            ast_node_type="else")
        self.assertEqual(
            "GOTO(else) "
            "position in code: (10, 20) - (10, 24)", str(statement))
        self.assertEqual(
            "Statement("
            "statement_type=StatementType.GOTO, "
            "ast_node_type=else, "
            "name=None, "
            "affected_by=set(), "
            "start_point=(10, 20), "
            "end_point=(10, 24))", repr(statement))

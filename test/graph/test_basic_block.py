__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/30'

from unittest import TestCase

from program_slicing.graph.basic_block import BasicBlock
from program_slicing.graph.statement import Statement, StatementType
from program_slicing.graph.point import Point


class BasicBlockTestCase(TestCase):

    def test_constructor(self):
        a = BasicBlock()
        self.assertEqual([], a.statements)
        statement_a = Statement(StatementType.UNKNOWN, Point(0, 0), Point(0, 1))
        statement_b = Statement(StatementType.UNKNOWN, Point(1, 1), Point(1, 2))
        a = BasicBlock(statements=[statement_a, statement_b])
        self.assertEqual([statement_a, statement_b], a.statements)

    def test_repr(self):
        statement_a = Statement(StatementType.UNKNOWN, Point(0, 0), Point(0, 1))
        statement_b = Statement(StatementType.UNKNOWN, Point(1, 1), Point(1, 2))
        basic_block = BasicBlock(statements=[statement_a, statement_b])
        self.assertEqual(
            "[Statement("
            "statement_type=StatementType.UNKNOWN, "
            "ast_node_type=None, "
            "name=None, "
            "affected_by=set(), "
            "start_point=(0, 0), "
            "end_point=(0, 1)), "
            "Statement("
            "statement_type=StatementType.UNKNOWN, "
            "ast_node_type=None, "
            "name=None, "
            "affected_by=set(), "
            "start_point=(1, 1), "
            "end_point=(1, 2))]", str(basic_block))
        self.assertEqual(
            "BasicBlock[Statement("
            "statement_type=StatementType.UNKNOWN, "
            "ast_node_type=None, "
            "name=None, "
            "affected_by=set(), "
            "start_point=(0, 0), "
            "end_point=(0, 1)), "
            "Statement("
            "statement_type=StatementType.UNKNOWN, "
            "ast_node_type=None, "
            "name=None, "
            "affected_by=set(), "
            "start_point=(1, 1), "
            "end_point=(1, 2))]", repr(basic_block))

    def test_is_empty(self):
        b = BasicBlock()
        self.assertTrue(b.is_empty())
        b = BasicBlock(statements=[Statement(StatementType.UNKNOWN, Point(0, 0), Point(0, 1))])
        self.assertFalse(b.is_empty())

    def test_append(self):
        a = BasicBlock()
        self.assertEqual([], a.statements)
        statement_a = Statement(StatementType.UNKNOWN, Point(0, 0), Point(0, 1))
        a.append(statement_a)
        self.assertEqual([statement_a], a.statements)
        statement_b = Statement(StatementType.UNKNOWN, Point(0, 0), Point(0, 1))
        a.append(statement_b)
        self.assertEqual([statement_a, statement_b], a.statements)

    def test_get_root(self):
        a = BasicBlock()
        self.assertIsNone(a.root)
        statement_a = Statement(StatementType.UNKNOWN, Point(0, 0), Point(0, 1))
        statement_b = Statement(StatementType.UNKNOWN, Point(1, 1), Point(1, 2))
        a = BasicBlock(statements=[statement_a, statement_b])
        self.assertEqual(statement_a, a.root)

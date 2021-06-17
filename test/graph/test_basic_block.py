__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/30'

from unittest import TestCase

from program_slicing.graph.basic_block import BasicBlock
from program_slicing.graph.statement import Statement, StatementType


class BasicBlockTestCase(TestCase):

    def test_constructor(self):
        a = BasicBlock()
        self.assertEqual([], a.statements)
        statement_a = Statement(StatementType.UNKNOWN, (0, 0), (0, 1))
        statement_b = Statement(StatementType.UNKNOWN, (1, 1), (1, 2))
        a = BasicBlock(statements=[statement_a, statement_b])
        self.assertEqual([statement_a, statement_b], a.statements)

    def test_is_empty(self):
        b = BasicBlock()
        self.assertTrue(b.is_empty())
        b = BasicBlock(statements=[Statement(StatementType.UNKNOWN, (0, 0), (0, 1))])
        self.assertFalse(b.is_empty())

    def test_append(self):
        a = BasicBlock()
        self.assertEqual([], a.statements)
        statement_a = Statement(StatementType.UNKNOWN, (0, 0), (0, 1))
        a.append(statement_a)
        self.assertEqual([statement_a], a.statements)
        statement_b = Statement(StatementType.UNKNOWN, (0, 0), (0, 1))
        a.append(statement_b)
        self.assertEqual([statement_a, statement_b], a.statements)

    def test_get_root(self):
        a = BasicBlock()
        self.assertIsNone(a.root)
        statement_a = Statement(StatementType.UNKNOWN, (0, 0), (0, 1))
        statement_b = Statement(StatementType.UNKNOWN, (1, 1), (1, 2))
        a = BasicBlock(statements=[statement_a, statement_b])
        self.assertEqual(statement_a, a.root)

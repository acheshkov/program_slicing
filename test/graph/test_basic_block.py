__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/30'

from unittest import TestCase

from program_slicing.graph.basic_block import BasicBlock
from program_slicing.graph.statement import Statement
from program_slicing.graph.statement import STATEMENT_TYPE_OBJECT


class BasicBlockTestCase(TestCase):

    def test_constructor(self):
        a = BasicBlock()
        self.assertEqual([], a.get_statements())
        statement_a = Statement(STATEMENT_TYPE_OBJECT, (0, 0), (0, 1))
        statement_b = Statement(STATEMENT_TYPE_OBJECT, (1, 1), (1, 2))
        a = BasicBlock(statements=[statement_a, statement_b])
        self.assertEqual([statement_a, statement_b], a.get_statements())

    def test_is_empty(self):
        b = BasicBlock()
        self.assertTrue(b.is_empty())
        b = BasicBlock(statements=[Statement(STATEMENT_TYPE_OBJECT, (0, 0), (0, 1))])
        self.assertFalse(b.is_empty())

    def test_append(self):
        a = BasicBlock()
        self.assertEqual([], a.get_statements())
        statement_a = Statement(STATEMENT_TYPE_OBJECT, (0, 0), (0, 1))
        a.append(statement_a)
        self.assertEqual([statement_a], a.get_statements())
        statement_b = Statement(STATEMENT_TYPE_OBJECT, (0, 0), (0, 1))
        a.append(statement_b)
        self.assertEqual([statement_a, statement_b], a.get_statements())

    def test_get_root(self):
        a = BasicBlock()
        self.assertIsNone(a.get_root())
        statement_a = Statement(STATEMENT_TYPE_OBJECT, (0, 0), (0, 1))
        statement_b = Statement(STATEMENT_TYPE_OBJECT, (1, 1), (1, 2))
        a = BasicBlock(statements=[statement_a, statement_b])
        self.assertEqual(statement_a, a.get_root())

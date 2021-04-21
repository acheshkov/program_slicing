__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/30'

from unittest import TestCase

from program_slicing.graph.basic_block import BasicBlock
from program_slicing.graph.cdg_node import CDGNode
from program_slicing.graph.cdg_node import CDG_NODE_TYPE_OBJECT


class BasicBlockTestCase(TestCase):

    def test_constructor(self):
        a = BasicBlock()
        self.assertEqual([], a.content)
        cdg_node_a = CDGNode("a", CDG_NODE_TYPE_OBJECT, (0, 0), (0, 1))
        cdg_node_b = CDGNode("b", CDG_NODE_TYPE_OBJECT, (1, 1), (1, 2))
        a = BasicBlock(content=[cdg_node_a, cdg_node_b])
        self.assertEqual([cdg_node_a, cdg_node_b], a.content)

    def test_is_empty(self):
        b = BasicBlock()
        self.assertTrue(b.is_empty())
        b.content = [CDGNode("a", CDG_NODE_TYPE_OBJECT, (0, 0), (0, 1))]
        self.assertFalse(b.is_empty())

    def test_append(self):
        a = BasicBlock()
        self.assertEqual([], a.content)
        cdg_node_a = CDGNode("a", CDG_NODE_TYPE_OBJECT, (0, 0), (0, 1))
        a.append(cdg_node_a)
        self.assertEqual([cdg_node_a], a.content)
        cdg_node_b = CDGNode("a", CDG_NODE_TYPE_OBJECT, (0, 0), (0, 1))
        a.append(cdg_node_b)
        self.assertEqual([cdg_node_a, cdg_node_b], a.content)

    def test_get_root(self):
        a = BasicBlock()
        self.assertIsNone(a.get_root())
        cdg_node_a = CDGNode("a", CDG_NODE_TYPE_OBJECT, (0, 0), (0, 1))
        cdg_node_b = CDGNode("b", CDG_NODE_TYPE_OBJECT, (1, 1), (1, 2))
        a = BasicBlock(content=[cdg_node_a, cdg_node_b])
        self.assertEqual(cdg_node_a, a.get_root())

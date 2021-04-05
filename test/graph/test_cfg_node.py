__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/30'

from unittest import TestCase
from program_slicing.graph.cfg_node import CFGNode
from program_slicing.graph.cdg_node import CDGNode
from program_slicing.graph.cdg_node import CDG_NODE_TYPE_OBJECT


class CGFNodeTestCase(TestCase):

    def test_constructor(self):
        a = CFGNode()
        self.assertEqual([], a.content)
        cdg_content_a = CDGNode("a", CDG_NODE_TYPE_OBJECT, (0, 0))
        cdg_content_b = CDGNode("b", CDG_NODE_TYPE_OBJECT, (1, 1))
        a = CFGNode(content=[cdg_content_a, cdg_content_b])
        self.assertEqual([cdg_content_a, cdg_content_b], a.content)

    def test_is_empty(self):
        b = CFGNode()
        self.assertTrue(b.is_empty())
        b.content = [CDGNode("a", CDG_NODE_TYPE_OBJECT, (0, 0))]
        self.assertFalse(b.is_empty())

    def test_append(self):
        a = CFGNode()
        self.assertEqual([], a.content)
        cdg_content_a = CDGNode("a", CDG_NODE_TYPE_OBJECT, (0, 0))
        a.append(cdg_content_a)
        self.assertEqual([cdg_content_a], a.content)
        cdg_content_b = CDGNode("a", CDG_NODE_TYPE_OBJECT, (0, 0))
        a.append(cdg_content_b)
        self.assertEqual([cdg_content_a, cdg_content_b], a.content)

    def test_get_root(self):
        a = CFGNode()
        self.assertIsNone(a.get_root())
        cdg_content_a = CDGNode("a", CDG_NODE_TYPE_OBJECT, (0, 0))
        cdg_content_b = CDGNode("b", CDG_NODE_TYPE_OBJECT, (1, 1))
        a = CFGNode(content=[cdg_content_a, cdg_content_b])
        self.assertEqual(cdg_content_a, a.get_root())

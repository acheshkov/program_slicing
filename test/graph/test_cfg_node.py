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

    def test_relations(self):
        cdg_node_a = CDGNode("a", CDG_NODE_TYPE_OBJECT, (0, 0))
        cdg_node_b = CDGNode("b", CDG_NODE_TYPE_OBJECT, (1, 1))
        cdg_node_c = CDGNode("c", CDG_NODE_TYPE_OBJECT, (2, 2))
        a = CFGNode(content=[cdg_node_a, cdg_node_b])
        self.assertFalse(a.is_empty())
        self.assertEqual([cdg_node_a, cdg_node_b], a.content)
        a.append(cdg_node_c)
        self.assertEqual([cdg_node_a, cdg_node_b, cdg_node_c], a.content)
        self.assertEqual(cdg_node_a, a.get_root())
        b = CFGNode()
        self.assertTrue(b.is_empty())

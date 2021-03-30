__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/30'

from unittest import TestCase
from program_slicing.parse.block import Block
from program_slicing.parse.node import Node, NODE_TYPE_OBJECT


class BlockTestCase(TestCase):

    def test_relations(self):
        node_a = Node("a", NODE_TYPE_OBJECT, (0, 0))
        node_b = Node("b", NODE_TYPE_OBJECT, (1, 1))
        node_c = Node("c", NODE_TYPE_OBJECT, (2, 2))
        node_d = Node("d", NODE_TYPE_OBJECT, (0, 2), children=[node_a, node_b, node_c])
        b = Block(nodes=[node_a, node_b])
        self.assertFalse(b.is_empty())
        self.assertEqual([node_a, node_b], b.nodes)
        b.append(node_c)
        self.assertEqual([node_a, node_b, node_c], b.nodes)
        self.assertEqual(node_a, b.get_root())
        self.assertEqual(node_d, b.get_cdg_parent())
        c = Block()
        self.assertTrue(c.is_empty())
        self.assertEqual(set(), b.get_cfg_parents())
        self.assertEqual(set(), c.get_cfg_parents())
        self.assertEqual(set(), b.children)
        self.assertEqual(set(), c.children)
        a = Block(children={b, c})
        self.assertEqual(set(), a.get_cfg_parents())
        self.assertEqual({b, c}, a.children)
        self.assertEqual({a}, b.get_cfg_parents())
        self.assertEqual({a}, c.get_cfg_parents())
        d = Block(parents={a})
        self.assertEqual(set(), a.get_cfg_parents())
        self.assertEqual({b, c, d}, a.children)
        self.assertEqual({a}, d.get_cfg_parents())
        e = Block()
        self.assertEqual(set(), e.get_cfg_parents())
        a.add_child(e)
        self.assertEqual({a}, e.get_cfg_parents())
        self.assertEqual({b, c, d, e}, a.children)

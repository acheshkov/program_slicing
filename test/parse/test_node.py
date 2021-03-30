__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/30'

from unittest import TestCase
from program_slicing.parse.node import Node, NODE_TYPE_OBJECT


class NodeTestCase(TestCase):

    def test_relations(self):
        b = Node("b", NODE_TYPE_OBJECT, (0, 0))
        c = Node("c", NODE_TYPE_OBJECT, (1, 1))
        self.assertIsNone(b.parent)
        self.assertIsNone(c.parent)
        self.assertEqual([], b.children)
        self.assertEqual([], c.children)
        a = Node("a", NODE_TYPE_OBJECT, (0, 2), children=[b, c])
        self.assertIsNone(a.parent)
        self.assertEqual([b, c], a.children)
        self.assertEqual(a, b.parent)
        self.assertEqual(a, c.parent)
        d = Node("d", NODE_TYPE_OBJECT, (2, 2))
        self.assertIsNone(d.parent)
        a.append(d)
        self.assertIsNone(a.parent)
        self.assertEqual([b, c, d], a.children)
        self.assertEqual(a, d.parent)

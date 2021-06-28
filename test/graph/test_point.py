__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/06/25'

from unittest import TestCase

from program_slicing.graph.point import Point


class PointCase(TestCase):

    def test_repr(self) -> None:
        a = Point(10, 20)
        self.assertEqual("(10, 20)", str(a))
        self.assertEqual("Point(10, 20)", repr(a))

    def test_operators(self) -> None:
        a = Point(10, 20)
        b = Point(20, 10)
        c = Point(10, 30)
        d = Point(10, 10)
        e = Point(10, 20)

        self.assertTrue(a == e)
        self.assertFalse(a == b)
        self.assertFalse(a == c)
        self.assertFalse(a == d)
        self.assertFalse(b == d)

        self.assertFalse(a != e)
        self.assertTrue(a != b)
        self.assertTrue(a != c)
        self.assertTrue(a != d)
        self.assertTrue(b != d)

        self.assertFalse(a < e)
        self.assertTrue(a < b)
        self.assertTrue(a < c)
        self.assertFalse(a < d)
        self.assertFalse(b < d)

        self.assertTrue(a <= e)
        self.assertTrue(a <= b)
        self.assertTrue(a <= c)
        self.assertFalse(a <= d)
        self.assertFalse(b <= d)

        self.assertFalse(a > e)
        self.assertFalse(a > b)
        self.assertFalse(a > c)
        self.assertTrue(a > d)
        self.assertTrue(b > d)

        self.assertTrue(a >= e)
        self.assertFalse(a >= b)
        self.assertFalse(a >= c)
        self.assertTrue(a >= d)
        self.assertTrue(b >= d)

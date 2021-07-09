__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/04/22'

from unittest import TestCase
import unittest

from program_slicing.graph.parse.pdg_java import parse


class PDGJavaTestCase(TestCase):

    @unittest.skip
    def test_parse(self) -> None:
        source_code = """
        class A {
            public static int main() {
                int n = 10;
                for(int i = 0; i < n; i += 1) {
                    if (i < 4) {
                        System.out.println("lol");
                        continue;
                    }
                    if (i > 6) {
                        System.out.println("che bu rek");
                        break;
                    }
                    else
                        System.out.println("kek");
                }
                return n;
            }
        }
        """
        pdg = parse(source_code)
        roots = pdg.entry_points
        self.assertIsNotNone(roots)
        self.assertEqual(1, len(roots))

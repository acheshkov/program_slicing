__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/04/20'

from unittest import TestCase

from program_slicing.graph.parse.ddg_java import parse


class CFGJavaTestCase(TestCase):

    def test_parse(self):
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
        ddg = parse(source_code)
        roots = ddg.get_entry_points()
        self.assertIsNotNone(roots)
        self.assertEqual(1, len(roots))

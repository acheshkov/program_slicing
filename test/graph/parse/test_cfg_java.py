__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/30'

from unittest import TestCase
from program_slicing.graph.parse.cfg_java import parse


class CFGJavaTestCase(TestCase):

    def test_parse(self):
        code = "class A {" \
               "    public static int main(){" \
               "        int n = 10;" \
               "        for(int i = 0; i < n; i += 1) {" \
               "            if (i > 4) {" \
               "                System.out.println(\"cheburek\");" \
               "                continue;" \
               "            }" \
               "            if (i < 6)" \
               "                System.out.println(\"lol\");" \
               "            else {" \
               "                System.out.println(\"kek\");" \
               "                break;" \
               "            }" \
               "        }" \
               "        return n;" \
               "    }" \
               "}"
        cfg = parse(code)
        roots = cfg.get_roots()
        self.assertIsNotNone(roots)
        self.assertEqual(0, len(roots))

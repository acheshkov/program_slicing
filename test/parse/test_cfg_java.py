__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/30'

from unittest import TestCase
from program_slicing.parse.cfg_java import parse


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
        root = cfg.root
        self.assertFalse(root in cfg.block)
        root = root.children[0]
        self.assertTrue(root in cfg.block)  # TODO: perhaps class declaration shouldn't be presented in a cfg
        root = root.children[0]
        self.assertTrue(root in cfg.block)  # TODO: perhaps function declaration shouldn't be presented in a cfg
        self.assertTrue(root.children[0] in cfg.block)
        self.assertTrue(root.children[1] in cfg.block)
        self.assertTrue(root.children[2] in cfg.block)
        self.assertTrue(root.children[3] in cfg.block)
        self.assertEqual(cfg.block[root.children[0]], cfg.block[root.children[1]])
        self.assertNotEqual(cfg.block[root.children[1]], cfg.block[root.children[2]])
        self.assertNotEqual(cfg.block[root.children[2]], cfg.block[root.children[3]])
        root = root.children[2]
        self.assertTrue(root in cfg.block)
        self.assertTrue(root.children[0] in cfg.block)
        self.assertTrue(root.children[1] in cfg.block)
        self.assertNotEqual(cfg.block[root.children[0]], cfg.block[root.children[1]])
        root = root.children[1]
        self.assertTrue(root in cfg.block)
        self.assertTrue(root.children[0] in cfg.block)
        self.assertTrue(root.children[1] in cfg.block)
        self.assertNotEqual(cfg.block[root.children[0]], cfg.block[root.children[1]])
        root = root.children[1]
        self.assertTrue(root in cfg.block)
        self.assertTrue(root.children[0] in cfg.block)
        self.assertTrue(root.children[1] in cfg.block)
        self.assertTrue(root.children[2] in cfg.block)
        self.assertNotEqual(cfg.block[root.children[0]], cfg.block[root.children[1]])
        self.assertNotEqual(cfg.block[root.children[1]], cfg.block[root.children[2]])
        root = root.children[2]
        self.assertTrue(root in cfg.block)
        self.assertTrue(root.children[0] in cfg.block)
        self.assertTrue(root.children[1] in cfg.block)
        self.assertNotEqual(cfg.block[root.children[0]], cfg.block[root.children[1]])
        root = root.children[0]
        self.assertTrue(root in cfg.block)
        root = root.children[0]
        self.assertTrue(root in cfg.block)

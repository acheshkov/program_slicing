__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/30'

from unittest import TestCase
from program_slicing.parse.cg_java import parse
from program_slicing.parse.node import \
    NODE_TYPE_FUNCTION, \
    NODE_TYPE_VARIABLE, \
    NODE_TYPE_ASSIGNMENT, \
    NODE_TYPE_CALL, \
    NODE_TYPE_STATEMENTS, \
    NODE_TYPE_BRANCH, \
    NODE_TYPE_LOOP, \
    NODE_TYPE_BREAK, \
    NODE_TYPE_GOTO, \
    NODE_TYPE_OBJECT, \
    NODE_TYPE_EXIT


class CGJavaTestCase(TestCase):

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
        cg = parse(code)
        root = cg.root
        self.assertEqual(NODE_TYPE_OBJECT, root.node_type)
        self.assertIsNotNone(root.children)
        self.assertEqual(1, len(root.children))
        self.assertFalse(root in cg.block)
        root = root.children[0]
        self.assertEqual(NODE_TYPE_OBJECT, root.node_type)
        self.assertIsNotNone(root.children)
        self.assertEqual(1, len(root.children))
        self.assertTrue(root in cg.block)  # TODO: perhaps class declaration shouldn't be presented in a cfg
        root = root.children[0]
        self.assertEqual(NODE_TYPE_FUNCTION, root.node_type)
        self.assertIsNotNone(root.children)
        self.assertEqual(4, len(root.children))
        self.assertTrue(root in cg.block)  # TODO: perhaps function declaration shouldn't be presented in a cfg
        self.assertTrue(root.children[0] in cg.block)
        self.assertTrue(root.children[1] in cg.block)
        self.assertTrue(root.children[2] in cg.block)
        self.assertTrue(root.children[3] in cg.block)
        self.assertEqual(cg.block[root.children[0]], cg.block[root.children[1]])
        self.assertNotEqual(cg.block[root.children[1]], cg.block[root.children[2]])
        self.assertNotEqual(cg.block[root.children[2]], cg.block[root.children[3]])
        self.assertEqual(NODE_TYPE_OBJECT, root.children[0].node_type)
        self.assertEqual(NODE_TYPE_VARIABLE, root.children[1].node_type)
        self.assertEqual(NODE_TYPE_EXIT, root.children[3].node_type)
        root = root.children[2]
        self.assertEqual(NODE_TYPE_LOOP, root.node_type)
        self.assertIsNotNone(root.children)
        self.assertEqual(2, len(root.children))
        self.assertTrue(root in cg.block)
        self.assertTrue(root.children[0] in cg.block)
        self.assertTrue(root.children[1] in cg.block)
        self.assertNotEqual(cg.block[root.children[0]], cg.block[root.children[1]])
        self.assertEqual(NODE_TYPE_OBJECT, root.children[0].node_type)
        self.assertEqual(NODE_TYPE_ASSIGNMENT, root.children[0].children[2].node_type)
        root = root.children[1]
        self.assertEqual(NODE_TYPE_STATEMENTS, root.node_type)
        self.assertIsNotNone(root.children)
        self.assertEqual(2, len(root.children))
        self.assertTrue(root in cg.block)
        self.assertTrue(root.children[0] in cg.block)
        self.assertTrue(root.children[1] in cg.block)
        self.assertNotEqual(cg.block[root.children[0]], cg.block[root.children[1]])
        self.assertEqual(NODE_TYPE_BRANCH, root.children[0].node_type)
        self.assertEqual(NODE_TYPE_GOTO, root.children[0].children[1].children[1].node_type)
        root = root.children[1]
        self.assertEqual(NODE_TYPE_BRANCH, root.node_type)
        self.assertIsNotNone(root.children)
        self.assertEqual(3, len(root.children))
        self.assertTrue(root in cg.block)
        self.assertTrue(root.children[0] in cg.block)
        self.assertTrue(root.children[1] in cg.block)
        self.assertTrue(root.children[2] in cg.block)
        self.assertNotEqual(cg.block[root.children[0]], cg.block[root.children[1]])
        self.assertNotEqual(cg.block[root.children[1]], cg.block[root.children[2]])
        self.assertEqual(NODE_TYPE_OBJECT, root.children[0].node_type)
        self.assertEqual(NODE_TYPE_OBJECT, root.children[1].node_type)
        root = root.children[2]
        self.assertEqual(NODE_TYPE_STATEMENTS, root.node_type)
        self.assertIsNotNone(root.children)
        self.assertEqual(2, len(root.children))
        self.assertTrue(root in cg.block)
        self.assertTrue(root.children[0] in cg.block)
        self.assertTrue(root.children[1] in cg.block)
        self.assertNotEqual(cg.block[root.children[0]], cg.block[root.children[1]])
        self.assertEqual(NODE_TYPE_BREAK, root.children[1].node_type)
        root = root.children[0]
        self.assertEqual(NODE_TYPE_OBJECT, root.node_type)
        self.assertIsNotNone(root.children)
        self.assertEqual(1, len(root.children))
        self.assertTrue(root in cg.block)
        root = root.children[0]
        self.assertEqual(NODE_TYPE_CALL, root.node_type)
        self.assertIsNotNone(root.children)
        self.assertEqual(1, len(root.children))
        self.assertTrue(root in cg.block)
        self.assertEqual(NODE_TYPE_OBJECT, root.children[0].node_type)

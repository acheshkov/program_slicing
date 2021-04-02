__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/30'

from unittest import TestCase
from program_slicing.graph.parse.cdg_java import parse
from program_slicing.graph.cdg_content import \
    CDG_CONTENT_TYPE_FUNCTION, \
    CDG_CONTENT_TYPE_VARIABLE, \
    CDG_CONTENT_TYPE_ASSIGNMENT, \
    CDG_CONTENT_TYPE_CALL, \
    CDG_CONTENT_TYPE_STATEMENTS, \
    CDG_CONTENT_TYPE_BRANCH, \
    CDG_CONTENT_TYPE_LOOP, \
    CDG_CONTENT_TYPE_BREAK, \
    CDG_CONTENT_TYPE_GOTO, \
    CDG_CONTENT_TYPE_OBJECT, \
    CDG_CONTENT_TYPE_EXIT


class CDGJavaTestCase(TestCase):

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
        cdg = parse(code)
        roots = cdg.get_entry_points()
        self.assertIsNotNone(roots)
        self.assertEqual(1, len(roots))
        root = roots.pop()
        self.assertEqual(CDG_CONTENT_TYPE_FUNCTION, root.content_type)
        children = [child for child in cdg.successors(root)]
        self.assertEqual(4, len(children))
        self.assertEqual(CDG_CONTENT_TYPE_OBJECT, children[0].content_type)
        self.assertEqual(CDG_CONTENT_TYPE_VARIABLE, children[1].content_type)
        self.assertEqual(CDG_CONTENT_TYPE_EXIT, children[3].content_type)
        root = children[2]
        self.assertEqual(CDG_CONTENT_TYPE_LOOP, root.content_type)
        children = [child for child in cdg.successors(root)]
        self.assertEqual(2, len(children))
        self.assertEqual(CDG_CONTENT_TYPE_OBJECT, children[0].content_type)
        self.assertEqual(CDG_CONTENT_TYPE_ASSIGNMENT, [child for child in cdg.successors(children[0])][2].content_type)
        root = children[1]
        self.assertEqual(CDG_CONTENT_TYPE_STATEMENTS, root.content_type)
        children = [child for child in cdg.successors(root)]
        self.assertEqual(2, len(children))
        self.assertEqual(CDG_CONTENT_TYPE_BRANCH, children[0].content_type)
        self.assertEqual(CDG_CONTENT_TYPE_GOTO, [child for child in cdg.successors(
            [child for child in cdg.successors(children[0])][1])][1].content_type)
        root = children[1]
        self.assertEqual(CDG_CONTENT_TYPE_BRANCH, root.content_type)
        children = [child for child in cdg.successors(root)]
        self.assertEqual(3, len(children))
        self.assertEqual(CDG_CONTENT_TYPE_OBJECT, children[0].content_type)
        self.assertEqual(CDG_CONTENT_TYPE_OBJECT, children[1].content_type)
        root = children[2]
        self.assertEqual(CDG_CONTENT_TYPE_STATEMENTS, root.content_type)
        children = [child for child in cdg.successors(root)]
        self.assertEqual(2, len(children))
        self.assertEqual(CDG_CONTENT_TYPE_BREAK, children[1].content_type)
        root = children[0]
        self.assertEqual(CDG_CONTENT_TYPE_OBJECT, root.content_type)
        children = [child for child in cdg.successors(root)]
        self.assertEqual(1, len(children))
        root = children[0]
        self.assertEqual(CDG_CONTENT_TYPE_CALL, root.content_type)
        children = [child for child in cdg.successors(root)]
        self.assertEqual(1, len(children))
        self.assertEqual(CDG_CONTENT_TYPE_OBJECT, children[0].content_type)

__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/04/02'

from unittest import TestCase

import networkx

from program_slicing.graph.manager import ProgramGraphsManager
from program_slicing.graph.parse import LANG_JAVA


class ManagerTestCase(TestCase):

    @staticmethod
    def __get_source_code_0():
        return "class A {" \
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

    @staticmethod
    def __get_manager_0():
        return ProgramGraphsManager(ManagerTestCase.__get_source_code_0(), LANG_JAVA)

    def test_init(self):
        pass

    def test_simple_blocks(self):
        pass

    def test_reach(self):
        mgr = self.__get_manager_0()
        assignments = [assignment for assignment in networkx.nodes(mgr.cfg)]
        self.assertEqual(0, len(assignments))

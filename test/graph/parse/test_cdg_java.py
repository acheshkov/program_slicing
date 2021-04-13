__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/30'

from unittest import TestCase

import networkx

from program_slicing.graph.parse import cdg_java
from program_slicing.graph.cdg import ControlDependenceGraph
from program_slicing.graph.cdg_node import CDGNode, \
    CDG_NODE_TYPE_FUNCTION, \
    CDG_NODE_TYPE_VARIABLE, \
    CDG_NODE_TYPE_LOOP, \
    CDG_NODE_TYPE_ASSIGNMENT, \
    CDG_NODE_TYPE_BRANCH, \
    CDG_NODE_TYPE_STATEMENTS, \
    CDG_NODE_TYPE_CALL, \
    CDG_NODE_TYPE_OBJECT, \
    CDG_NODE_TYPE_GOTO, \
    CDG_NODE_TYPE_EXIT


class CDGJavaTestCase(TestCase):

    @staticmethod
    def __get_source_code_0():
        return """
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

    @staticmethod
    def __get_cdg_0():
        entry_point = CDGNode("", CDG_NODE_TYPE_FUNCTION, start_point=(2, 4), end_point=(18, 1), name="main")
        variable_n = CDGNode("", CDG_NODE_TYPE_VARIABLE, start_point=(3, 8), end_point=(3, 18), name="n")
        assign_n_0_left = CDGNode("", CDG_NODE_TYPE_OBJECT, start_point=(3, 12), end_point=(3, 13), name="n")
        assign_n_0_right = CDGNode("", CDG_NODE_TYPE_OBJECT, start_point=(3, 16), end_point=(3, 18), name="10")
        assign_n_0 = CDGNode("", CDG_NODE_TYPE_ASSIGNMENT, start_point=(3, 13), end_point=(3, 18), name="=")
        variable_i = CDGNode("", CDG_NODE_TYPE_VARIABLE, start_point=(4, 12), end_point=(4, 21), name="i")
        assign_i_0_left = CDGNode("", CDG_NODE_TYPE_OBJECT, start_point=(4, 16), end_point=(4, 17), name="i")
        assign_i_0_right = CDGNode("", CDG_NODE_TYPE_OBJECT, start_point=(4, 20), end_point=(4, 21), name="0")
        assign_i_0 = CDGNode("", CDG_NODE_TYPE_ASSIGNMENT, start_point=(4, 16), end_point=(4, 21), name="=")
        loop = CDGNode("", CDG_NODE_TYPE_LOOP, start_point=(4, 8), end_point=(15, 9), name="for")
        loop_condition_left = CDGNode("", CDG_NODE_TYPE_OBJECT, start_point=(4, 23), end_point=(4, 24), name="i")
        loop_condition_right = CDGNode("", CDG_NODE_TYPE_OBJECT, start_point=(4, 27), end_point=(4, 28), name="n")
        loop_condition = CDGNode("", CDG_NODE_TYPE_OBJECT, start_point=(4, 23), end_point=(4, 28), name="<")
        loop_body = CDGNode("", CDG_NODE_TYPE_STATEMENTS, start_point=(4, 38), end_point=(15, 8))
        branch_0 = CDGNode("", CDG_NODE_TYPE_BRANCH, start_point=(5, 12), end_point=(8, 13), name="if")
        branch_0_condition_left = CDGNode("", CDG_NODE_TYPE_OBJECT, start_point=(5, 16), end_point=(5, 17), name="i")
        branch_0_condition_right = CDGNode("", CDG_NODE_TYPE_OBJECT, start_point=(5, 20), end_point=(5, 21), name="4")
        branch_0_condition = CDGNode("", CDG_NODE_TYPE_OBJECT, start_point=(5, 16), end_point=(5, 21), name="<")
        branch_0_body = CDGNode("", CDG_NODE_TYPE_STATEMENTS, start_point=(5, 23), end_point=(8, 12))
        call_0_arg = CDGNode("", CDG_NODE_TYPE_OBJECT, start_point=(6, 35), end_point=(6, 40), name="\"lol\"")
        call_0 = CDGNode("", CDG_NODE_TYPE_CALL, start_point=(6, 16), end_point=(6, 41), name="System.out.println")
        goto_continue = CDGNode("", CDG_NODE_TYPE_GOTO, start_point=(7, 16), end_point=(7, 24), name="continue")
        branch_1 = CDGNode("", CDG_NODE_TYPE_BRANCH, start_point=(9, 12), end_point=(14, 41), name="if")
        branch_1_condition_left = CDGNode("", CDG_NODE_TYPE_OBJECT, start_point=(9, 16), end_point=(9, 17), name="i")
        branch_1_condition_right = CDGNode("", CDG_NODE_TYPE_OBJECT, start_point=(9, 20), end_point=(9, 21), name="6")
        branch_1_condition = CDGNode("", CDG_NODE_TYPE_OBJECT, start_point=(9, 16), end_point=(9, 21), name=">")
        branch_1_body = CDGNode("", CDG_NODE_TYPE_STATEMENTS, start_point=(9, 23), end_point=(12, 13))
        call_1_arg = CDGNode("", CDG_NODE_TYPE_OBJECT, start_point=(10, 35), end_point=(10, 47), name="\"che bu rek\"")
        call_1 = CDGNode("", CDG_NODE_TYPE_CALL, start_point=(10, 16), end_point=(10, 48), name="System.out.println")
        goto_break = CDGNode("", CDG_NODE_TYPE_GOTO, start_point=(11, 16), end_point=(11, 21), name="break")
        call_2_arg = CDGNode("", CDG_NODE_TYPE_OBJECT, start_point=(12, 35), end_point=(12, 40), name="\"kek\"")
        call_2 = CDGNode("", CDG_NODE_TYPE_CALL, start_point=(12, 16), end_point=(12, 41), name="System.out.println")
        assign_i_1_left = CDGNode("", CDG_NODE_TYPE_OBJECT, start_point=(4, 30), end_point=(4, 31), name="i")
        assign_i_1_right = CDGNode("", CDG_NODE_TYPE_OBJECT, start_point=(4, 35), end_point=(4, 36), name="1")
        assign_i_1 = CDGNode("", CDG_NODE_TYPE_ASSIGNMENT, start_point=(4, 30), end_point=(4, 36), name="+=")
        obj_return_value = CDGNode("", CDG_NODE_TYPE_OBJECT, start_point=(14, 15), end_point=(14, 16), name="n")
        obj_return = CDGNode("", CDG_NODE_TYPE_EXIT, start_point=(14, 8), end_point=(14, 16), name="return")

        cdg = ControlDependenceGraph()
        cdg.add_node(entry_point)
        cdg.add_node(variable_n)
        cdg.add_node(assign_n_0_left)
        cdg.add_node(assign_n_0_right)
        cdg.add_node(assign_n_0)
        cdg.add_node(variable_i)
        cdg.add_node(assign_i_0_left)
        cdg.add_node(assign_i_0_right)
        cdg.add_node(assign_i_0)
        cdg.add_node(loop)
        cdg.add_node(loop_condition_left)
        cdg.add_node(loop_condition_right)
        cdg.add_node(loop_condition)
        cdg.add_node(loop_body)
        cdg.add_node(branch_0)
        cdg.add_node(branch_0_condition_left)
        cdg.add_node(branch_0_condition_right)
        cdg.add_node(branch_0_condition)
        cdg.add_node(branch_0_body)
        cdg.add_node(call_0_arg)
        cdg.add_node(call_0)
        cdg.add_node(goto_continue)
        cdg.add_node(branch_1)
        cdg.add_node(branch_1_condition_left)
        cdg.add_node(branch_1_condition_right)
        cdg.add_node(branch_1_condition)
        cdg.add_node(branch_1_body)
        cdg.add_node(call_1_arg)
        cdg.add_node(call_1)
        cdg.add_node(goto_break)
        cdg.add_node(call_2_arg)
        cdg.add_node(call_2)
        cdg.add_node(assign_i_1_left)
        cdg.add_node(assign_i_1_right)
        cdg.add_node(assign_i_1)
        cdg.add_node(obj_return_value)
        cdg.add_node(obj_return)

        cdg.add_edge(entry_point, variable_n)
        cdg.add_edge(entry_point, assign_n_0_left)
        cdg.add_edge(entry_point, assign_n_0_right)
        cdg.add_edge(entry_point, assign_n_0)
        cdg.add_edge(entry_point, variable_i)
        cdg.add_edge(entry_point, assign_i_0_left)
        cdg.add_edge(entry_point, assign_i_0_right)
        cdg.add_edge(entry_point, assign_i_0)
        cdg.add_edge(entry_point, loop)
        cdg.add_edge(entry_point, loop_condition_left)
        cdg.add_edge(entry_point, loop_condition_right)
        cdg.add_edge(entry_point, loop_condition)
        cdg.add_edge(loop_condition, loop_body)
        cdg.add_edge(loop_condition, branch_0)
        cdg.add_edge(loop_condition, branch_0_condition_left)
        cdg.add_edge(loop_condition, branch_0_condition_right)
        cdg.add_edge(loop_condition, branch_0_condition)
        cdg.add_edge(branch_0_condition, branch_0_body)
        cdg.add_edge(branch_0_condition, call_0_arg)
        cdg.add_edge(branch_0_condition, call_0)
        cdg.add_edge(branch_0_condition, goto_continue)
        cdg.add_edge(loop_condition, branch_1)
        cdg.add_edge(loop_condition, branch_1_condition_left)
        cdg.add_edge(loop_condition, branch_1_condition_right)
        cdg.add_edge(loop_condition, branch_1_condition)
        cdg.add_edge(branch_1_condition, branch_1_body)
        cdg.add_edge(branch_1_condition, call_1_arg)
        cdg.add_edge(branch_1_condition, call_1)
        cdg.add_edge(branch_1_condition, goto_break)
        cdg.add_edge(branch_1_condition, call_2_arg)
        cdg.add_edge(branch_1_condition, call_2)
        cdg.add_edge(loop_condition, assign_i_1_left)
        cdg.add_edge(loop_condition, assign_i_1_right)
        cdg.add_edge(loop_condition, assign_i_1)
        cdg.add_edge(entry_point, obj_return_value)
        cdg.add_edge(entry_point, obj_return)

        cdg.control_flow = {
            entry_point: [variable_n],
            variable_n: [assign_n_0_left],
            assign_n_0_left: [assign_n_0_right],
            assign_n_0_right: [assign_n_0],
            assign_n_0: [variable_i],
            variable_i: [assign_i_0_left],
            assign_i_0_left: [assign_i_0_right],
            assign_i_0_right: [assign_i_0],
            assign_i_0: [loop],
            loop: [loop_condition_left],
            loop_condition_left: [loop_condition_right],
            loop_condition_right: [loop_condition],
            loop_condition: [loop_body, obj_return_value],
            loop_body: [branch_0],
            branch_0: [branch_0_condition_left],
            branch_0_condition_left: [branch_0_condition_right],
            branch_0_condition_right: [branch_0_condition],
            branch_0_condition: [branch_0_body, branch_1],
            branch_0_body: [call_0_arg],
            call_0_arg: [call_0],
            call_0: [goto_continue],
            goto_continue: [assign_i_1_left],
            branch_1: [branch_1_condition_left],
            branch_1_condition_left: [branch_1_condition_right],
            branch_1_condition_right: [branch_1_condition],
            branch_1_condition: [branch_1_body, call_2_arg],
            branch_1_body: [call_1_arg],
            call_1_arg: [call_1],
            call_1: [goto_break],
            goto_break: [obj_return_value],
            call_2_arg: [call_2],
            call_2: [assign_i_1_left],
            assign_i_1_left: [assign_i_1_right],
            assign_i_1_right: [assign_i_1],
            assign_i_1: [loop],
            obj_return_value: [obj_return]
        }
        cdg.add_entry_point(entry_point)
        return cdg

    def test_parse(self):
        self.assertTrue(networkx.is_isomorphic(self.__get_cdg_0(), cdg_java.parse(self.__get_source_code_0())))

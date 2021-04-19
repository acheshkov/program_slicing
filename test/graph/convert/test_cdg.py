__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/04/02'

from unittest import TestCase

import networkx

from program_slicing.graph.parse import cdg_java
from program_slicing.graph.cfg import ControlFlowGraph
from program_slicing.graph import convert


class CDGTestCase(TestCase):

    @staticmethod
    def __get_cdg_and_cfg_0():
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
        cdg = cdg_java.parse(source_code)
        cfg = ControlFlowGraph()
        cfg.add_edges_from([
            ("2_4_var_n_and_i", "4_4_for_condition"),
            ("4_4_for_condition", "4_5_first_if"),
            ("4_4_for_condition", "16_16_return"),
            ("4_5_first_if", "5_7_print_and_continue"),
            ("4_5_first_if", "9_9_second_if"),
            ("5_7_print_and_continue", "4_4_update_i"),
            ("9_9_second_if", "9_11_print_and_break"),
            ("9_9_second_if", "14_14_last_print"),
            ("9_11_print_and_break", "16_16_return"),
            ("14_14_last_print", "4_4_update_i"),
            ("4_4_update_i", "4_4_for_condition"),
        ])
        return cdg, cfg

    @staticmethod
    def __get_cdg_and_cfg_1():
        source_code = """
        class A {
            int main(String args) {
                try {
                    a = args[10];
                }
                catch (Exception e) {
                    e.printStackTrace();
                }
                catch (MyException e) {
                }
                finally {
                    System.out.println("The 'try catch' is finished.");
                }
            }
        }
        """
        cdg = cdg_java.parse(source_code)
        cfg = ControlFlowGraph()
        cfg.add_edges_from([
            ("2_5_try", "6_6_catch"),
            ("2_5_try", "11_11_finally"),
            ("6_6_catch", "9_9_catch"),
            ("6_6_catch", "6_8_stack_trace"),
            ("6_8_stack_trace", "11_11_finally"),
            ("9_9_catch", "11_11_finally"),
            ("9_9_catch", "9_10_empty_block"),
            ("9_10_empty_block", "11_11_finally")
        ])
        return cdg, cfg

    def test_convert_cdg_to_cfg_isomorphic(self):
        cdg, cfg = self.__get_cdg_and_cfg_0()
        self.assertTrue(networkx.is_isomorphic(cfg, convert.cdg.to_cfg(cdg)))
        cdg, cfg = self.__get_cdg_and_cfg_1()
        a = convert.cdg.to_cfg(cdg)
        self.assertTrue(networkx.is_isomorphic(cfg, convert.cdg.to_cfg(cdg)))

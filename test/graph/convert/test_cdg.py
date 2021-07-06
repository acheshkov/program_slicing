__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/04/02'

from unittest import TestCase

import networkx

from program_slicing.graph.parse import cdg_java
from program_slicing.graph.cfg import ControlFlowGraph
from program_slicing.graph.ddg import DataDependenceGraph
from program_slicing.graph import convert
from program_slicing.graph.statement import StatementType


class CDGTestCase(TestCase):

    @staticmethod
    def __get_cdg_0():
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
        return cdg_java.parse(source_code)

    @staticmethod
    def __get_cfg_0():
        cfg = DataDependenceGraph()
        cfg.add_edges_from([
            ("2_4_var_n_and_i", "4_4_for_condition"),
            ("4_4_for_condition", "4_5_first_if"),
            ("4_4_for_condition", "16_16_return"),
            ("4_5_first_if", "5_7_print_and_continue"),
            ("4_5_first_if", "9_9_second_if"),
            ("5_7_print_and_continue", "4_4_update_i"),
            ("9_9_second_if", "9_11_print_and_break"),
            ("9_9_second_if", "13_14_last_print"),
            ("9_11_print_and_break", "16_16_return"),
            ("13_14_last_print", "4_4_update_i"),
            ("4_4_update_i", "4_4_for_condition"),
        ])
        return cfg

    @staticmethod
    def __get_ddg_0():
        ddg = DataDependenceGraph()
        ddg.add_edges_from([
            ("int n = 10", "loop"),
            ("int n = 10", "i < n"),
            ("int n = 10", "n from i < n"),
            ("int i = 0", "i < n"),
            ("int i = 0", "i from i < n"),
            ("int i = 0", "loop body"),
            ("int i = 0", "if (i < 4)"),
            ("int i = 0", "(i < 4)"),
            ("int i = 0", "i < 4"),
            ("int i = 0", "i from i < 4"),
            ("int i = 0", "i += 1"),
            ("int i = 0", "i from i += 1"),
            ("int i = 0", "if (i > 6)"),
            ("int i = 0", "(i > 6)"),
            ("int i = 0", "i > 6"),
            ("int i = 0", "i from i > 6"),
            ("i += 1", "i < n"),
            ("i += 1", "i from i < n"),
            ("i += 1", "loop body"),
            ("i += 1", "if (i < 4)"),
            ("i += 1", "(i < 4)"),
            ("i += 1", "i < 4"),
            ("i += 1", "i from i < 4"),
            ("i += 1", "i += 1"),
            ("i += 1", "i from i += 1"),
            ("i += 1", "if (i > 6)"),
            ("i += 1", "(i > 6)"),
            ("i += 1", "i > 6"),
            ("i += 1", "i from i > 6"),
            ("int n = 10", "return n"),
            ("int n = 10", "n from return n"),
            ("int n = 10", "exit_point")
        ])
        ddg.add_nodes_from(range(36))
        return ddg

    @staticmethod
    def __get_pdg_0():
        pdg = CDGTestCase.__get_ddg_0()
        pdg.add_edge(0, "int n = 10")
        pdg.add_edge(0, "int i = 0")
        pdg.add_edge(0, "i < n")
        pdg.add_edge(0, "i from i < n")
        pdg.add_edge(0, "n from i < n")
        pdg.add_edge(0, "loop")
        pdg.add_edge(0, "n from return n")
        pdg.add_edge(0, "return n")
        pdg.add_edge(0, "exit_point")
        pdg.add_edge("loop", "loop body")
        pdg.add_edge("loop", "(i < 4)")
        pdg.add_edge("loop", "i < 4")
        pdg.add_edge("loop", "i from i < 4")
        pdg.add_edge("loop", "if (i < 4)")
        pdg.add_edge("loop", "(i > 6)")
        pdg.add_edge("loop", "i > 6")
        pdg.add_edge("loop", "i from i > 6")
        pdg.add_edge("loop", "if (i > 6)")
        pdg.add_edge("loop", "i += 1")
        pdg.add_edge("loop", "i from i += 1")
        pdg.add_nodes_from(range(36, 40))
        pdg.add_edges_from([(0, i) for i in range(1, 8)])
        pdg.add_edges_from([("loop", i) for i in range(8, 11)])
        pdg.add_edges_from([("if (i < 4)", i) for i in range(11, 20)])
        pdg.add_edges_from([("if (i > 6)", i) for i in range(20, 37)])
        return pdg

    @staticmethod
    def __get_cdg_1():
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
        return cdg_java.parse(source_code)

    @staticmethod
    def __get_cfg_1():
        cfg = ControlFlowGraph()
        cfg.add_edges_from([
            ("2_3_try", "6_6_catch"),
            ("2_3_try", "3_5_assign"),
            ("3_5_assign", "11_11_finally"),
            ("6_6_catch", "9_9_catch"),
            ("6_6_catch", "6_8_stack_trace"),
            ("6_8_stack_trace", "11_11_finally"),
            ("9_9_catch", "11_11_finally"),
            ("9_9_catch", "9_10_empty_block"),
            ("9_10_empty_block", "11_11_finally")
        ])
        return cfg

    @staticmethod
    def __get_ddg_1():
        ddg = DataDependenceGraph()
        ddg.add_edges_from([
            ("Exception e", "first catch body"),
            ("Exception e", "e.printStackTrace();"),
            ("Exception e", "e.printStackTrace()"),
            ("Exception e", "e from e.printStackTrace()"),
            ("MyException e", "catch (MyException e)"),
        ])
        ddg.add_nodes_from(range(26))
        return ddg

    @staticmethod
    def __get_pdg_1():
        pdg = CDGTestCase.__get_cdg_1()
        for variable_statement in pdg:
            if variable_statement.statement_type != StatementType.VARIABLE:
                continue
            for statement in pdg:
                if statement.statement_type != StatementType.VARIABLE and \
                        variable_statement.name in statement.affected_by and \
                        (variable_statement.start_point.line_number >= 9 and statement.start_point.line_number >= 9 or
                         variable_statement.start_point.line_number < 9 and statement.start_point.line_number < 9):
                    pdg.add_edge(variable_statement, statement)
        return pdg

    @staticmethod
    def __get_cdg_2():
        source_code = """
        final FlipNode flipNode = (FlipNode) node;
        context.getVariableCompiler().retrieveLocalVariable(flipNode.getIndex(), flipNode.getDepth());
        if (flipNode.isExclusive()) {
            context.performBooleanBranch(new BranchCallback() {
                public void branch(BodyCompiler context) {
                }
            }, new BranchCallback() {
                public void branch(BodyCompiler context) {
                }
            });
        }
        """
        return cdg_java.parse(source_code)

    @staticmethod
    def __get_cfg_2():
        cfg = ControlFlowGraph()
        cfg.add_edge("1_3_beginning", "3_10_block")
        cfg.add_edge("1_3_beginning", "11_11_ending")
        cfg.add_edge("3_10_block", "11_11_ending")
        cfg.add_node("5_6_block")
        cfg.add_node("8_9_block")
        return cfg

    @staticmethod
    def __get_ddg_2():
        ddg = DataDependenceGraph()
        ddg.add_edges_from([
            ("flipNode", "context...;"),
            ("flipNode", "context"),
            ("flipNode", "(flipNode.getIndex(), flipNode.getDepth())"),
            ("flipNode", "flipNode.getIndex()"),
            ("flipNode", "flipNode.getDepth()"),
            ("flipNode", "flipNode.getIndex"),
            ("flipNode", "flipNode.getDepth"),
            ("flipNode", "if (flipNode.isExclusive())"),
            ("flipNode", "(flipNode.isExclusive())"),
            ("flipNode", "flipNode.isExclusive()"),
            ("flipNode", "flipNode.isExclusive")
        ])
        ddg.add_nodes_from(range(30))
        return ddg

    @staticmethod
    def __get_pdg_2():
        pdg = CDGTestCase.__get_cdg_2()
        variable_statement = [statement for statement in pdg if statement.statement_type == StatementType.VARIABLE][0]
        for statement in pdg:
            if statement.statement_type != StatementType.VARIABLE and variable_statement.name in statement.affected_by:
                pdg.add_edge(variable_statement, statement)
        return pdg

    def test_convert_cdg_to_cfg_isomorphic(self):
        cdg = self.__get_cdg_0()
        cfg = self.__get_cfg_0()
        self.assertTrue(networkx.is_isomorphic(cfg, convert.cdg.to_cfg(cdg)))
        cdg = self.__get_cdg_1()
        cfg = self.__get_cfg_1()
        self.assertTrue(networkx.is_isomorphic(cfg, convert.cdg.to_cfg(cdg)))
        cdg = self.__get_cdg_2()
        cfg = self.__get_cfg_2()
        self.assertTrue(networkx.is_isomorphic(cfg, convert.cdg.to_cfg(cdg)))

    def test_convert_cdg_to_ddg_isomorphic(self):
        cdg = self.__get_cdg_0()
        ddg = self.__get_ddg_0()
        self.assertTrue(networkx.is_isomorphic(ddg, convert.cdg.to_ddg(cdg)))
        cdg = self.__get_cdg_1()
        ddg = self.__get_ddg_1()
        self.assertTrue(networkx.is_isomorphic(ddg, convert.cdg.to_ddg(cdg)))
        cdg = self.__get_cdg_2()
        ddg = self.__get_ddg_2()
        self.assertTrue(networkx.is_isomorphic(ddg, convert.cdg.to_ddg(cdg)))

    def test_convert_cdg_to_pdg_isomorphic(self):
        cdg = self.__get_cdg_0()
        pdg = self.__get_pdg_0()
        self.assertTrue(networkx.is_isomorphic(pdg, convert.cdg.to_pdg(cdg)))
        cdg = self.__get_cdg_1()
        pdg = self.__get_pdg_1()
        self.assertTrue(networkx.is_isomorphic(pdg, convert.cdg.to_pdg(cdg)))
        cdg = self.__get_cdg_2()
        pdg = self.__get_pdg_2()
        self.assertTrue(networkx.is_isomorphic(pdg, convert.cdg.to_pdg(cdg)))

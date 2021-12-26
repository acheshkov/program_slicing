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
            ("int n = 10", "n from return n")
        ])
        ddg.add_node("exit_point")
        ddg.add_node("loop body")
        ddg.add_nodes_from(range(20))
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
        pdg.add_edge(0, "parameters")
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
        pdg.add_nodes_from(range(20, 23))
        pdg.add_edges_from([(0, i) for i in range(1, 6)])
        pdg.add_edges_from([("loop", i) for i in range(6, 9)])
        pdg.add_edges_from([("if (i < 4)", i) for i in range(9, 13)])
        pdg.add_edges_from([("if (i > 6)", i) for i in range(13, 20)])
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
            ("Exception e", "e.printStackTrace();"),
            ("Exception e", "e.printStackTrace()"),
            ("MyException e", "catch (MyException e)"),
            ("String args", "a = args[10];"),
            ("String args", "a = args[10]"),
            ("String args", "args[10]"),
        ])
        ddg.add_nodes_from(range(15))
        return ddg

    @staticmethod
    def __get_pdg_1():
        pdg = CDGTestCase.__get_cdg_1()
        for variable_statement in pdg:
            if variable_statement.statement_type not in {StatementType.VARIABLE, StatementType.OBJECT}:
                continue
            for statement in pdg:
                if statement.statement_type not in {StatementType.VARIABLE, StatementType.OBJECT} and \
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
        return cfg

    @staticmethod
    def __get_ddg_2():
        ddg = DataDependenceGraph()
        ddg.add_edges_from([
            ("flipNode", "context...;"),
            ("flipNode", "context"),
            ("flipNode", "if (flipNode.isExclusive())"),
            ("flipNode", "(flipNode.isExclusive())"),
            ("flipNode", "flipNode.isExclusive()")
        ])
        ddg.add_nodes_from(range(6))
        return ddg

    @staticmethod
    def __get_pdg_2():
        pdg = CDGTestCase.__get_cdg_2()
        variable_statement = [statement for statement in pdg if statement.statement_type == StatementType.OBJECT][0]
        for statement in pdg:
            if statement.statement_type != StatementType.OBJECT and variable_statement.name in statement.affected_by:
                pdg.add_edge(variable_statement, statement)
        return pdg

    @staticmethod
    def __get_cdg_3():
        source_code = """
        class A {
            void main() {
                {
                    int a = 0;
                }
                {
                    int a = 1;
                }
                for (int a = 2; a < n;) {
                    foo(a);
                }
                for (int a = 22; a < 10 * n; a++) {
                    boo(a);
                }
                try (int a = 3) {
                }
                finally {
                }
                try {
                    int a = 4;
                }
                catch (Exception a) {
                    a.printStackTrace();
                }
            }
        }
        """
        return cdg_java.parse(source_code)

    @staticmethod
    def __get_cfg_3():
        cfg = ControlFlowGraph()
        cfg.add_edge("2_9_beginning", "9_9_for")
        cfg.add_edge("9_9_for", "9_11_block")
        cfg.add_edge("9_11_block", "9_9_for")
        cfg.add_edge("9_9_for", "12_12_for_init")
        cfg.add_edge("12_12_for_init", "12_12_for")
        cfg.add_edge("12_12_for", "12_14_block")
        cfg.add_edge("12_14_block", "12_12_for")
        cfg.add_edge("12_12_for", "15_15_try")
        cfg.add_edge("15_15_try", "15_16_block")
        cfg.add_edge("15_15_try", "17_19_finally_and_try")
        cfg.add_edge("15_16_block", "17_19_finally_and_try")
        cfg.add_edge("17_19_finally_and_try", "19_21_block")
        cfg.add_edge("17_19_finally_and_try", "22_22_catch")
        cfg.add_edge("19_21_block", "exit")
        cfg.add_edge("22_22_catch", "exit")
        cfg.add_edge("22_22_catch", "22_24_block")
        cfg.add_edge("22_24_block", "exit")
        return cfg

    @staticmethod
    def __get_ddg_3():
        ddg = DataDependenceGraph()
        ddg.add_edges_from([
            ("int a = 2", "a < n"),
            ("int a = 2", "a from a < n"),
            ("int a = 2", "9_9_for"),
            ("int a = 2", "foo(a);"),
            ("int a = 2", "foo(a)"),
            ("int a = 22", "a < 10 * n"),
            ("int a = 22", "a from a < 10 * n"),
            ("int a = 22", "12_12_for"),
            ("int a = 22", "boo(a);"),
            ("int a = 22", "boo(a)"),
            ("int a = 22", "a++"),
            ("int a = 22", "a from a++"),
            ("a++", "a < 10 * n"),
            ("a++", "a from a < 10 * n"),
            ("a++", "12_12_for"),
            ("a++", "boo(a);"),
            ("a++", "boo(a)"),
            ("a++", "a++"),
            ("a++", "a from a++"),
            ("Exception a", "catch"),
            ("Exception a", "a.printStackTrace();"),
            ("Exception a", "a.printStackTrace()")
        ])
        ddg.add_nodes_from(range(35))
        return ddg

    @staticmethod
    def __get_pdg_3():
        pdg = CDGTestCase.__get_cdg_3()
        for variable_statement in pdg:
            if variable_statement.statement_type not in {
                StatementType.VARIABLE,
                StatementType.OBJECT,
                StatementType.ASSIGNMENT
            }:
                continue
            for statement in pdg:
                if statement.statement_type not in {StatementType.VARIABLE, StatementType.OBJECT} and \
                        statement.ast_node_type != "local_variable_declaration" and \
                        variable_statement.name in statement.affected_by and \
                        (9 <= variable_statement.start_point.line_number <= 11 and
                         9 <= statement.start_point.line_number <= 11 or
                         12 <= variable_statement.start_point.line_number <= 14 and
                         12 <= statement.start_point.line_number <= 14 or
                         22 <= variable_statement.start_point.line_number <= 24 and
                         22 <= statement.start_point.line_number <= 24):
                    pdg.add_edge(variable_statement, statement)
        return pdg

    @staticmethod
    def graph_to_str(graph):
        result = []
        for node in graph:
            successors = [str(successor) for successor in graph.successors(node)]
            if successors:
                result.append(str(node) + ":\n\t" + "\n\t".join(successors))
        # result.append("")
        # for node in graph:
        #     successors = [str(successor) for successor in graph.successors(node)]
        #     if not successors:
        #         result.append(str(node))
        return "\n".join(result)

    def assertIsomorphic(self, graph1, graph2) -> None:
        self.maxDiff = None
        if not networkx.is_isomorphic(graph1, graph2):
            self.assertEqual(CDGTestCase.graph_to_str(graph1), CDGTestCase.graph_to_str(graph2))

    def test_convert_cdg_to_cfg_isomorphic(self):
        cdg = self.__get_cdg_0()
        cfg = self.__get_cfg_0()
        self.assertIsomorphic(cfg, convert.cdg.to_cfg(cdg))
        cdg = self.__get_cdg_1()
        cfg = self.__get_cfg_1()
        self.assertIsomorphic(cfg, convert.cdg.to_cfg(cdg))
        cdg = self.__get_cdg_2()
        cfg = self.__get_cfg_2()
        self.assertIsomorphic(cfg, convert.cdg.to_cfg(cdg))
        cdg = self.__get_cdg_3()
        cfg = self.__get_cfg_3()
        self.assertIsomorphic(cfg, convert.cdg.to_cfg(cdg))

    def test_convert_cdg_to_ddg_isomorphic(self):
        cdg = self.__get_cdg_0()
        ddg = self.__get_ddg_0()
        self.assertIsomorphic(ddg, convert.cdg.to_ddg(cdg))
        cdg = self.__get_cdg_1()
        ddg = self.__get_ddg_1()
        self.assertIsomorphic(ddg, convert.cdg.to_ddg(cdg))
        cdg = self.__get_cdg_2()
        ddg = self.__get_ddg_2()
        self.assertIsomorphic(ddg, convert.cdg.to_ddg(cdg))
        cdg = self.__get_cdg_3()
        ddg = self.__get_ddg_3()
        self.assertIsomorphic(ddg, convert.cdg.to_ddg(cdg))

    def test_convert_cdg_to_pdg_isomorphic(self):
        cdg = self.__get_cdg_0()
        pdg = self.__get_pdg_0()
        self.assertIsomorphic(pdg, convert.cdg.to_pdg(cdg))
        cdg = self.__get_cdg_1()
        pdg = self.__get_pdg_1()
        self.assertIsomorphic(pdg, convert.cdg.to_pdg(cdg))
        cdg = self.__get_cdg_2()
        pdg = self.__get_pdg_2()
        self.assertIsomorphic(pdg, convert.cdg.to_pdg(cdg))
        cdg = self.__get_cdg_3()
        pdg = self.__get_pdg_3()
        self.assertIsomorphic(pdg, convert.cdg.to_pdg(cdg))

__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/04/02'

from unittest import TestCase

from program_slicing.graph.manager import ProgramGraphsManager
from program_slicing.graph.parse import LANG_JAVA


class ManagerTestCase(TestCase):

    @staticmethod
    def __get_source_code_0() -> str:
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
    def __get_manager_0() -> ProgramGraphsManager:
        return ProgramGraphsManager(ManagerTestCase.__get_source_code_0(), LANG_JAVA)

    def test_init(self) -> None:
        pass

    def test_basic_blocks(self) -> None:
        mgr = self.__get_manager_0()
        blocks = [block for block in mgr.get_control_flow_graph()]
        self.assertEqual(9, len(blocks))
        for block in blocks:
            for statement in block:
                self.assertEqual(block, mgr.get_basic_block(statement))

    def test_dom(self) -> None:
        mgr = self.__get_manager_0()
        cfg = mgr.get_control_flow_graph()
        self.assertEqual(1, len(cfg.entry_points))
        block_with_n = [entry_point for entry_point in cfg.entry_points][0]
        block_with_for = [child for child in cfg.successors(block_with_n)][0]
        block_with_first_if = [child for child in cfg.successors(block_with_for)][0]
        block_with_continue = [child for child in cfg.successors(block_with_first_if)][0]
        block_with_second_if = [child for child in cfg.successors(block_with_first_if)][1]
        block_with_break = [child for child in cfg.successors(block_with_second_if)][0]
        block_with_else = [child for child in cfg.successors(block_with_second_if)][1]
        block_with_update_i = [child for child in cfg.successors(block_with_else)][0]
        block_with_return = [child for child in cfg.successors(block_with_for)][1]

        all_blocks = {
            block_with_n,
            block_with_for,
            block_with_first_if,
            block_with_continue,
            block_with_second_if,
            block_with_break,
            block_with_else,
            block_with_update_i,
            block_with_return
        }
        self.assertEqual(all_blocks, mgr.get_dominated_blocks(block_with_n))
        self.assertEqual(all_blocks, mgr.get_dominated_blocks(block_with_for))
        self.assertEqual(all_blocks, mgr.get_dominated_blocks(block_with_return))
        for_blocks = {
            block_with_first_if,
            block_with_continue,
            block_with_second_if,
            block_with_break,
            block_with_else,
            block_with_update_i
        }
        self.assertEqual(for_blocks, mgr.get_dominated_blocks(block_with_first_if))
        self.assertEqual(for_blocks, mgr.get_dominated_blocks(block_with_second_if))
        self.assertEqual(for_blocks, mgr.get_dominated_blocks(block_with_update_i))
        first_if_blocks = {
            block_with_continue
        }
        self.assertEqual(first_if_blocks, mgr.get_dominated_blocks(block_with_continue))
        second_if_blocks = {
            block_with_break,
            block_with_else
        }
        self.assertEqual(second_if_blocks, mgr.get_dominated_blocks(block_with_break))
        self.assertEqual(second_if_blocks, mgr.get_dominated_blocks(block_with_else))

    def test_reach(self) -> None:
        mgr = self.__get_manager_0()
        cfg = mgr.get_control_flow_graph()
        self.assertEqual(1, len(cfg.entry_points))
        block_with_n = [entry_point for entry_point in cfg.entry_points][0]
        block_with_for = [child for child in cfg.successors(block_with_n)][0]
        block_with_first_if = [child for child in cfg.successors(block_with_for)][0]
        block_with_continue = [child for child in cfg.successors(block_with_first_if)][0]
        block_with_second_if = [child for child in cfg.successors(block_with_first_if)][1]
        block_with_break = [child for child in cfg.successors(block_with_second_if)][0]
        block_with_else = [child for child in cfg.successors(block_with_second_if)][1]
        block_with_update_i = [child for child in cfg.successors(block_with_else)][0]
        block_with_return = [child for child in cfg.successors(block_with_for)][1]
        self.assertEqual({
            block_with_n,
            block_with_for,
            block_with_first_if,
            block_with_continue,
            block_with_second_if,
            block_with_break,
            block_with_else,
            block_with_update_i,
            block_with_return
        }, mgr.get_reach_blocks(block_with_n))
        self.assertEqual({
            block_with_for,
            block_with_first_if,
            block_with_continue,
            block_with_second_if,
            block_with_break,
            block_with_else,
            block_with_update_i,
            block_with_return
        }, mgr.get_reach_blocks(block_with_for))
        self.assertEqual({
            block_with_first_if,
            block_with_continue,
            block_with_second_if,
            block_with_break,
            block_with_else,
            block_with_update_i,
            block_with_return
        }, mgr.get_reach_blocks(block_with_first_if))
        self.assertEqual({
            block_with_continue,
            block_with_update_i
        }, mgr.get_reach_blocks(block_with_continue))
        self.assertEqual({
            block_with_second_if,
            block_with_break,
            block_with_else,
            block_with_update_i,
            block_with_return
        }, mgr.get_reach_blocks(block_with_second_if))
        self.assertEqual({
            block_with_break,
            block_with_return
        }, mgr.get_reach_blocks(block_with_break))
        self.assertEqual({
            block_with_else,
            block_with_update_i
        }, mgr.get_reach_blocks(block_with_else))
        self.assertEqual({
            block_with_update_i,
        }, mgr.get_reach_blocks(block_with_update_i))
        self.assertEqual({
            block_with_return,
        }, mgr.get_reach_blocks(block_with_return))

    def test_boundary_blocks(self) -> None:
        mgr = self.__get_manager_0()
        cfg = mgr.get_control_flow_graph()
        self.assertEqual(1, len(cfg.entry_points))
        block_with_n = [entry_point for entry_point in cfg.entry_points][0]
        block_with_for = [child for child in cfg.successors(block_with_n)][0]
        block_with_first_if = [child for child in cfg.successors(block_with_for)][0]
        block_with_continue = [child for child in cfg.successors(block_with_first_if)][0]
        block_with_second_if = [child for child in cfg.successors(block_with_first_if)][1]
        block_with_break = [child for child in cfg.successors(block_with_second_if)][0]
        block_with_else = [child for child in cfg.successors(block_with_second_if)][1]
        block_with_update_i = [child for child in cfg.successors(block_with_else)][0]
        block_with_return = [child for child in cfg.successors(block_with_for)][1]
        self.assertEqual({
            block_with_n
        }, mgr.get_boundary_blocks(block_with_n))
        self.assertEqual({
            block_with_n,
            block_with_for
        }, mgr.get_boundary_blocks(block_with_for))
        self.assertEqual({
            block_with_n,
            block_with_for,
            block_with_first_if
        }, mgr.get_boundary_blocks(block_with_first_if))
        self.assertEqual({
            block_with_n,
            block_with_for,
            block_with_first_if,
            block_with_continue
        }, mgr.get_boundary_blocks(block_with_continue))
        self.assertEqual({
            block_with_n,
            block_with_for,
            block_with_first_if,
            block_with_second_if
        }, mgr.get_boundary_blocks(block_with_second_if))
        self.assertEqual({
            block_with_n,
            block_with_for,
            block_with_first_if,
            block_with_second_if,
            block_with_break
        }, mgr.get_boundary_blocks(block_with_break))
        self.assertEqual({
            block_with_n,
            block_with_for,
            block_with_first_if,
            block_with_second_if,
            block_with_else
        }, mgr.get_boundary_blocks(block_with_else))
        self.assertEqual({
            block_with_n,
            block_with_for,
            block_with_first_if,
            block_with_second_if,
            block_with_update_i,
        }, mgr.get_boundary_blocks(block_with_update_i))
        self.assertEqual({
            block_with_n,
            block_with_for,
            block_with_return,
        }, mgr.get_boundary_blocks(block_with_return))

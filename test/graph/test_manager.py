__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/04/02'

from unittest import TestCase

from program_slicing.graph.manager import ProgramGraphsManager
from program_slicing.graph.parse import Lang


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
        return ProgramGraphsManager(ManagerTestCase.__get_source_code_0(), Lang.JAVA)

    def test_init(self) -> None:
        pass

    def test_basic_blocks(self) -> None:
        mgr = self.__get_manager_0()
        blocks = [block for block in mgr.control_flow_graph]
        self.assertEqual(9, len(blocks))
        for block in blocks:
            for statement in block:
                self.assertEqual(block, mgr.get_basic_block(statement))

    def test_dom(self) -> None:
        mgr = self.__get_manager_0()
        cfg = mgr.control_flow_graph
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
        cfg = mgr.control_flow_graph
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
        cfg = mgr.control_flow_graph
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

    def test_identify_unique_block_with_if(self) -> None:
        if_statement = '''
        if (workspace == null) {
            return Collections.emptySet();
        }
        '''
        manager = ProgramGraphsManager(if_statement, Lang.JAVA)
        self.assertEqual(4, len(list(manager.scope_statements)))

    def test_identify_unique_block_with_for_each(self) -> None:
        for_each_block = '''
        for (LaunchConfiguration config: workspace.getLaunchConfigurations()) { int i = 0;}
        '''
        manager = ProgramGraphsManager(for_each_block, Lang.JAVA)
        self.assertEqual(3, len(list(manager.scope_statements)))

    def test_identify_unique_block_with_while(self) -> None:
        while_block = '''
        while (null != (line = input.readLine()) && maxLines > 0) {
                maxLines--;
        }'''
        manager = ProgramGraphsManager(while_block, Lang.JAVA)
        self.assertEqual(3, len(list(manager.scope_statements)))

    def test_identify_unique_block_with_sync(self) -> None:
        sync_block = '''
        synchronized (getLock(cache)) {
           url = cache.toURI().toURL();
        }'''
        manager = ProgramGraphsManager(sync_block, Lang.JAVA)
        self.assertEqual(3, len(list(manager.scope_statements)))

    def test_identify_unique_block_with_for(self) -> None:
        for_cycle_block = '''
        for (int i = 0; i < 10; ++i) {
            foo();
        }'''
        manager = ProgramGraphsManager(for_cycle_block, Lang.JAVA)
        self.assertEqual(3, len(list(manager.scope_statements)))

    def test_identify_unique_block_without_brackets(self) -> None:
        block_without_brackets = '''
        for (int i = 0; i < 10; ++i)
            foo();
        '''
        manager = ProgramGraphsManager(block_without_brackets, Lang.JAVA)
        self.assertEqual(2, len(list(manager.scope_statements)))

    def test_identify_unique_blocks_with_try(self) -> None:
        block_without_try = '''
            try (int resource = getResources()) {
                tracker.waitForAll(resource);
            } catch (Exception e) {
                int i = 0;
            }
            finally {
                int j = 0;
            }
        '''
        manager = ProgramGraphsManager(block_without_try, Lang.JAVA)
        self.assertEqual(6, len(list(manager.scope_statements)))

    def test_identify_unique_blocks_with_anonymous_class(self) -> None:
        block_without_try = '''
        HelloWorld englishGreeting = new EnglishGreeting();

        HelloWorld frenchGreeting = new HelloWorld() {
            public void greet() {
                greetSomeone("tout le monde");
            }
            public void greetSomeone(String someone) {
                name = someone;
                System.out.println("Salut " + name);
            }
        };
        '''
        manager = ProgramGraphsManager(block_without_try, Lang.JAVA)
        self.assertEqual(1, len(list(manager.scope_statements)))

    def test_identify_unique_blocks_with_lambda(self) -> None:
        block_with_lambda = '''
            MyPrinter myPrinter = (s) -> { System.out.println(s); };
        '''
        manager = ProgramGraphsManager(block_with_lambda, Lang.JAVA)
        self.assertEqual(1, len(list(manager.scope_statements)))

    def test_identify_unique_block_with_break(self) -> None:
        while_block = '''
        for (String s: strings) {
             a();
             b();
             if (true) { break;}
        }
        while (i < 3 ) {
             a();
             b();
             outer_loop:
             for (;;) {
                if (true) {
                    if(true) {
                       break outer_loop;
                    }
                 }
            }
        }
        '''
        manager = ProgramGraphsManager(while_block, Lang.JAVA)
        self.assertEqual(13, len(list(manager.scope_statements)))

    def test_identify_unique_block_with_continue(self) -> None:
        while_block = '''
        for (String s: strings) {
             a();
             b();
             if (true) { continue;}
        }
        '''
        manager = ProgramGraphsManager(while_block, Lang.JAVA)
        self.assertEqual(5, len(list(manager.scope_statements)))

    def test_statements_in_range_continuous(self) -> None:
        code = '''
        for (int i=0; i < 10; i++){
            continue;
        }
        '''
        manager = ProgramGraphsManager(code, Lang.JAVA)
        [root_statement] = manager.program_dependence_graph.entry_points
        self.assertEqual({1, 2, 3}, manager.get_statement_line_numbers(root_statement))

    def test_all_statements_with_empty_lines_loop(self) -> None:
        code = '''

            for (int i=0; i < 10; i++){

                continue;

            }

        '''
        manager = ProgramGraphsManager(code, Lang.JAVA)
        [root_statement] = manager.program_dependence_graph.entry_points
        self.assertEqual({2, 4, 6}, manager.get_statement_line_numbers(root_statement))

    def test_all_statements_with_empty_lines_branch(self) -> None:
        code = '''

            if (a < 5) {

                --a;

            }

        '''
        manager = ProgramGraphsManager(code, Lang.JAVA)
        [root_statement] = manager.program_dependence_graph.entry_points
        self.assertEqual({2, 4, 6}, manager.get_statement_line_numbers(root_statement))

    def test_all_statements_with_inline_comments(self) -> None:
        code = '''
            // comment
            for (int i=0; i < 10; i++){
                // comment
                continue;
                // comment
            }

        '''
        manager = ProgramGraphsManager(code, Lang.JAVA)
        [root_statement] = manager.program_dependence_graph.entry_points
        self.assertEqual({2, 4, 6}, manager.get_statement_line_numbers(root_statement))

    def test_all_statements_with_multiline_comments(self) -> None:
        code = '''
            for (int i=0; i < 10; i++){
                /*
                    comment
                */
                continue;
            }

        '''
        manager = ProgramGraphsManager(code, Lang.JAVA)
        [root_statement] = manager.program_dependence_graph.entry_points
        self.assertEqual({1, 5, 6}, manager.get_statement_line_numbers(root_statement))

    def test_all_statements_comments_and_empty_lines(self) -> None:
        code = '''
            for (int i=0; i < 10; i++){

                // abort
                continue;
            }

        '''
        manager = ProgramGraphsManager(code, Lang.JAVA)
        [root_statement] = manager.program_dependence_graph.entry_points
        self.assertEqual({1, 4, 5}, manager.get_statement_line_numbers(root_statement))

__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/06/01'

import unittest
from unittest import TestCase

from program_slicing.decomposition.block_slicing import build_opportunities_filtered, __build_statements_in_scope
from program_slicing.graph.parse import LANG_JAVA
from program_slicing.graph.manager import ProgramGraphsManager
from program_slicing.graph.point import Point

build_statements_in_scope = __build_statements_in_scope


class BlockSlicingTestCase(TestCase):
    def test_identify_unique_block_with_if(self) -> None:
        if_statement = '''
        if (workspace == null) {
            return Collections.emptySet();
        }
        '''
        manager = ProgramGraphsManager(if_statement, LANG_JAVA)
        self.assertEqual(4, len(build_statements_in_scope(manager)))

    def test_identify_unique_block_with_for_each(self) -> None:
        for_each_block = '''
        for (LaunchConfiguration config: workspace.getLaunchConfigurations()) { int i = 0;}
        '''
        manager = ProgramGraphsManager(for_each_block, LANG_JAVA)
        self.assertEqual(3, len(build_statements_in_scope(manager)))

    def test_identify_unique_block_with_while(self) -> None:
        while_block = '''
        while (null != (line = input.readLine()) && maxLines > 0) {
                maxLines--;
        }'''
        manager = ProgramGraphsManager(while_block, LANG_JAVA)
        self.assertEqual(3, len(build_statements_in_scope(manager)))

    def test_identify_unique_block_with_sync(self) -> None:
        sync_block = '''
        synchronized (getLock(cache)) {
           url = cache.toURI().toURL();
        }'''
        manager = ProgramGraphsManager(sync_block, LANG_JAVA)
        self.assertEqual(3, len(build_statements_in_scope(manager)))

    def test_identify_unique_block_with_for(self) -> None:
        for_cycle_block = '''
        for (int i = 0; i < 10; ++i) {
            foo();
        }'''
        manager = ProgramGraphsManager(for_cycle_block, LANG_JAVA)
        self.assertEqual(3, len(build_statements_in_scope(manager)))

    def test_identify_unique_block_without_brackets(self) -> None:
        block_without_brackets = '''
        for (int i = 0; i < 10; ++i)
            foo();
        '''
        manager = ProgramGraphsManager(block_without_brackets, LANG_JAVA)
        self.assertEqual(2, len(build_statements_in_scope(manager)))

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
        manager = ProgramGraphsManager(block_without_try, LANG_JAVA)
        self.assertEqual(6, len(build_statements_in_scope(manager)))

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
        manager = ProgramGraphsManager(block_without_try, LANG_JAVA)
        self.assertEqual(5, len(build_statements_in_scope(manager)))

    def test_identify_unique_blocks_with_lambda(self) -> None:
        block_without_lambda = '''
            MyPrinter myPrinter = (s) -> { System.out.println(s); };
        '''
        manager = ProgramGraphsManager(block_without_lambda, LANG_JAVA)
        self.assertEqual(2, len(build_statements_in_scope(manager)))

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
        manager = ProgramGraphsManager(while_block, LANG_JAVA)
        self.assertEqual(13, len(build_statements_in_scope(manager)))

    def test_identify_unique_block_with_continue(self) -> None:
        while_block = '''
        for (String s: strings) {
             a();
             b();
             if (true) { continue;}
        }
        '''
        manager = ProgramGraphsManager(while_block, LANG_JAVA)
        self.assertEqual(5, len(build_statements_in_scope(manager)))

    def test_opportunities_ranges(self):
        expected_opportunities = {
            ((1, 8), (28, 9)), ((1, 8), (29, 59)), ((1, 8), (39, 10)), ((1, 8), (14, 9)),
            ((2, 8), (14, 9)), ((2, 8), (28, 9)), ((2, 8), (29, 59)), ((2, 8), (39, 10)),
            ((3, 8), (14, 9)), ((3, 8), (28, 9)), ((3, 8), (29, 59)), ((3, 8), (39, 10)),
            ((3, 8), (41, 51)),
            ((5, 8), (14, 9)), ((5, 8), (28, 9)), ((5, 8), (29, 59)), ((5, 8), (39, 10)),
            ((5, 8), (41, 51)), ((5, 8), (43, 34)),
            ((16, 8), (28, 9)), ((16, 8), (29, 59)), ((16, 8), (39, 10)), ((16, 8), (41, 51)),
            ((16, 8), (43, 34)), ((16, 8), (46, 34)), ((16, 8), (47, 17)),
            ((17, 12), (26, 13)),
            ((18, 12), (26, 13)),
            ((19, 16), (25, 17)),
            ((29, 8), (39, 10)), ((29, 8), (41, 51)), ((29, 8), (43, 34)), ((29, 8), (46, 34)),
            ((29, 8), (47, 17)),
            ((31, 8), (39, 10)), ((31, 8), (41, 51)), ((31, 8), (43, 34)), ((31, 8), (46, 34)),
            ((31, 8), (47, 17)),
            ((41, 8), (46, 34)), ((41, 8), (47, 17)), ((42, 8), (47, 17))}
        self.t_ = '''
        int t = 12;
        fImage= loadImage("logo.gif");
        MediaTracker tracker= new MediaTracker(this);

        try {
            tracker.waitForAll();
            System.out.println(1);
        } catch (Exception e) {
            int i = 0;
            ++i;
        } finally {
            int j = 0;
            ++j;
        }

        for (int i = 0; i < 10; ++i) {
            foo();
            while(b < 10) {
                if (i < 8) {
                    System.out.println(b);
                    System.out.println(i);
                }
                else {
                    System.out.println(i);
                }
            }

        }
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

        ArrayList<String> strs = new ArrayList<>();
        for (String s: strs)
            System.out.println(s);

        while(b < 10)
            System.out.println(s);
        return t;'''
        found_opportunities = {
            ((program_slice.ranges[0][0].line_number, program_slice.ranges[0][0].column_number),
             (program_slice.ranges[-1][1].line_number, program_slice.ranges[-1][1].column_number))
            for program_slice in build_opportunities_filtered(
                self.t_,
                LANG_JAVA,
                min_amount_of_lines=5,
                max_percentage_of_lines=0.8
            ) if program_slice.ranges}
        self.assertEqual(expected_opportunities, found_opportunities)

    def test_else_blocks(self) -> None:
        code = '''
        if (problems != null) {
            int max = problems.length;
            StringBuffer buffer = new StringBuffer(25);
            int count = 0;
            for (int i = 0; i < max; i++) {
                CategorizedProblem problem = problems[i];
                if ((problem != null) && (problem.isError())) {
                    buffer.append("\t"  +problem.getMessage() + "\n" );
                    count++;
                    if (problemLine == 0) {
                        problemLine = problem.getSourceLineNumber();
                    }
                    else {
                        problemLine = problem.getSourceLineNumber();
                        func();
                        func();
                        func();
                    }
                    problems[i] = null;
                }
            }
            if (count > 1) {
                buffer.insert(0, Messages.compilation_unresolvedProblems);
            } else {
                buffer.insert(0, Messages.compilation_unresolvedProblem);
                func();
            }
            problemString = buffer.toString();
        }
        '''
        found_opportunities = {
            (program_slice.ranges[0][0].line_number, program_slice.ranges[-1][1].line_number)
            for program_slice in build_opportunities_filtered(code, LANG_JAVA)
        }
        self.assertTrue((15, 16) in found_opportunities, True)
        self.assertTrue((15, 17) in found_opportunities, True)
        self.assertTrue((15, 18) in found_opportunities, True)
        self.assertTrue((26, 27) in found_opportunities, True)

    def test_opportunities_with_range_number(self):
        code = '''
        if (problems != null) {
            int max = problems.length;
            StringBuffer buffer = new StringBuffer(25);
            int count = 0;
            for (int i = 0; i < max; i++) {
                CategorizedProblem problem = problems[i];
                if ((problem != null) && (problem.isError())) {
                    buffer.append("\t"  +problem.getMessage() + "\n" );
                    count++;
                    if (problemLine == 0) {
                        problemLine = problem.getSourceLineNumber();
                    }
                    else {
                        problemLine = problem.getSourceLineNumber();
                    }
                    problems[i] = null;
                }
            }
            if (count > 1) {
                buffer.insert(0, Messages.compilation_unresolvedProblems);
            } else {
                buffer.insert(0, Messages.compilation_unresolvedProblem);
            }
            problemString = buffer.toString();
        }
        '''
        all_lines = code.split('\n')
        max_percentage = 0.8
        found_opportunities = {
            (program_slice.ranges[0][0].line_number, program_slice.ranges[-1][1].line_number)
            for program_slice in build_opportunities_filtered(
                code, LANG_JAVA, min_amount_of_lines=5, max_percentage_of_lines=max_percentage)
        }
        self.assertEqual([], [x for x in found_opportunities if x[1] - x[0] < 4])
        self.assertEqual([], [x for x in found_opportunities if (len(all_lines) / x[1] - x[0]) > max_percentage])
        max_percentage = 0
        found_opportunities = {
            (program_slice.ranges[0][0].line_number, program_slice.ranges[-1][1].line_number)
            for program_slice in build_opportunities_filtered(
                code, LANG_JAVA, min_amount_of_lines=5, max_percentage_of_lines=max_percentage)
        }
        self.assertEqual(set(), found_opportunities)

    @unittest.skip("If block is strange")
    def test_opportunities_with_else_if(self):
        code = '''
            if (count > 1) {
                buffer.insert(0, Messages.compilation_unresolvedProblems);
                buffer.insert(0, Messages.compilation_unresolvedProblems);
                buffer.insert(0, Messages.compilation_unresolvedProblems);
                buffer.insert(0, Messages.compilation_unresolvedProblems);
                buffer.insert(0, Messages.compilation_unresolvedProblems);

            } else if (count > 2) {
                buffer.insert(0, Messages.compilation_unresolvedProblem);
                buffer.insert(0, Messages.compilation_unresolvedProblem);
                buffer.insert(0, Messages.compilation_unresolvedProblem);
                buffer.insert(0, Messages.compilation_unresolvedProblem);
                buffer.insert(0, Messages.compilation_unresolvedProblem);

            }
            else {
                buffer.insert(0, Messages.compilation_unresolvedProblem);
                buffer.insert(0, Messages.compilation_unresolvedProblem);
                buffer.insert(0, Messages.compilation_unresolvedProblem);
                buffer.insert(0, Messages.compilation_unresolvedProblem);
                buffer.insert(0, Messages.compilation_unresolvedProblem);
            }
        }
        '''
        found_opportunities = {
            (program_slice.ranges[0][0], program_slice.ranges[-1][1])
            for program_slice in build_opportunities_filtered(
                code, LANG_JAVA, min_amount_of_lines=5, max_percentage_of_lines=1.00)
        }
        expected = {
            (Point(9, 16), Point(13, 73)), (Point(17, 16), Point(21, 73)), (Point(1, 12), Point(22, 13)),
            (Point(2, 16), Point(6, 74)), (Point(9, 0), Point(13, 0))}

        self.assertEqual(found_opportunities, expected)

    def test_opportunities_filter_scope(self):
        code = '''
            for(int i = 0; i < 5; ++i) {
                int j = 0;
                int m = 0;
                find();
                find();
                find(m);
                find(j);
            }
        '''
        found_opportunities = {
            (program_slice.ranges[0][0].line_number, program_slice.ranges[-1][1].line_number)
            for program_slice in build_opportunities_filtered(code, LANG_JAVA)
        }
        # ignore opportunities where we have 2 var declarations
        # and there are lines in the current scope which is depended on
        # those var declarations
        self.assertTrue((2, 3) not in found_opportunities, True)
        self.assertTrue((2, 4) not in found_opportunities, True)
        self.assertTrue((2, 5) not in found_opportunities, True)

    def test_filter_with_usage_inside_inner_scope(self):
        code_with_usage_inside_inner_scope = '''
            for(int i = 0; i < 5; ++i) {
                int j = 0;
                int m = 0;
                for(int k = 0; k < 5; ++k) {
                    for(int u = 0; u < 5; ++u) {
                        find();
                        find();
                        find();
                        find();
                        find(m);
                        find(j);
                    }
                }
            }
        '''
        found_opportunities = {
            (program_slice.ranges[0][0].line_number, program_slice.ranges[-1][1].line_number)
            for program_slice in build_opportunities_filtered(code_with_usage_inside_inner_scope, LANG_JAVA)
        }
        # ignore opportunities where we have 2 var declarations
        # and there are lines in the inner scope which is depended on
        # those var declarations
        self.assertTrue((2, 3) not in found_opportunities, True)
        self.assertTrue((2, 4) not in found_opportunities, True)
        self.assertTrue((2, 5) not in found_opportunities, True)
        self.assertTrue((2, 6) not in found_opportunities, True)
        self.assertTrue((2, 7) not in found_opportunities, True)
        self.assertTrue((2, 8) not in found_opportunities, True)
        self.assertTrue((2, 9) not in found_opportunities, True)

    def test_do_not_filter_complex_objects(self):
        complex_objects = '''
            Object h = new Object();
            for(int i = 0; i < 5; ++i) {
                Finder j = new Finder();
                Shalala s = new Shalala();
                int b = 0;
                find();
                find();
                h.append(b);
                j.call();
            }
        '''
        found_opportunities = {
            (program_slice.ranges[0][0].line_number, program_slice.ranges[-1][1].line_number)
            for program_slice in build_opportunities_filtered(
                complex_objects, LANG_JAVA, min_amount_of_lines=2, max_percentage_of_lines=0.8)
        }
        self.assertEqual({
            (1, 10),
            (2, 10),
            (3, 4), (3, 8), (3, 9),
            (4, 5), (4, 6), (4, 7), (4, 8), (4, 9),
            (5, 6), (5, 7), (5, 8), (5, 9),
            (6, 7), (6, 8), (6, 9),
            (7, 8), (7, 9),
            (8, 9)},
            found_opportunities)

    def test_do_not_filter_with_diff_scope(self):
        diff_scope = '''
            Object h = new Object();
            for(int i = 0; i < 5; ++i) {
                for(int k = 0; k < 5; ++k) {
                    int b = 0;
                    find();
                    find();
                    find();
                    find();
                    h.append(b);
                }
                for(int j= 0; j < 5; ++j) {
                    int a = 0;
                    int b = 0;
                    find();
                    find();
                    --b;
                    ++a;
                }
            }
        '''
        found_opportunities = {
            (program_slice.ranges[0][0].line_number, program_slice.ranges[-1][1].line_number)
            for program_slice in build_opportunities_filtered(diff_scope, LANG_JAVA)
        }
        self.assertTrue((4, 5) in found_opportunities)
        self.assertTrue((4, 6) in found_opportunities)
        self.assertTrue((4, 7) in found_opportunities)
        self.assertTrue((4, 8) in found_opportunities)
        self.assertTrue((4, 9) in found_opportunities)

    def test_filter_with_immutable_classes(self):
        diff_scope = '''
            Object h = new Object();
            for(int i = 0; i < 5; ++i) {
                int b = 0;
                Integer a = b;
                find();
                find();
                find();
                func(b);
                System.out.println(a);
            }
        '''
        found_opportunities = {
            (program_slice.ranges[0][0].line_number, program_slice.ranges[-1][1].line_number)
            for program_slice in build_opportunities_filtered(diff_scope, LANG_JAVA)
        }
        self.assertTrue((3, 4) not in found_opportunities)
        self.assertTrue((3, 5) not in found_opportunities)
        self.assertTrue((3, 6) not in found_opportunities)
        self.assertTrue((3, 7) not in found_opportunities)

    def test_filter_with_assignment_usage(self):
        diff_scope = '''
            Object h = new Object();
            for(int i = 0; i < 5; ++i) {
                int b = 0;
                Integer a = b;
                find();
                find();
                --b;
                a = b * 2;
                System.out.println(a);
            }
        '''
        found_opportunities = {
            (program_slice.ranges[0][0].line_number, program_slice.ranges[-1][1].line_number)
            for program_slice in build_opportunities_filtered(diff_scope, LANG_JAVA)
        }
        self.assertTrue((3, 4) not in found_opportunities)
        self.assertTrue((3, 5) not in found_opportunities)
        self.assertTrue((3, 6) not in found_opportunities)
        self.assertTrue((3, 7) not in found_opportunities)

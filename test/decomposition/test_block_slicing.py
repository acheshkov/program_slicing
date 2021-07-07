__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/06/01'

from unittest import TestCase

from program_slicing.decomposition import block_slicing
from program_slicing.decomposition.block_slicing import get_block_slices
from program_slicing.graph.parse import LANG_JAVA


determine_unique_blocks = block_slicing.__determine_unique_blocks


class BlockSlicingTestCase(TestCase):

    def test_identify_unique_block_with_if(self) -> None:
        if_statement = '''
        if (workspace == null) {
            return Collections.emptySet();
        }
        '''
        blocks, _ = determine_unique_blocks(if_statement, LANG_JAVA)
        self.assertEqual(2, len(blocks))

    def test_identify_unique_block_with_for_each(self) -> None:
        for_each_block = '''
        for (LaunchConfiguration config: workspace.getLaunchConfigurations()) { int i = 0;}
        '''
        blocks, _ = determine_unique_blocks(for_each_block, LANG_JAVA)
        self.assertEqual(2, len(blocks))

    def test_identify_unique_block_with_while(self) -> None:
        while_block = '''
        while (null != (line = input.readLine()) && maxLines > 0) {
                maxLines--;
        }'''
        blocks, _ = determine_unique_blocks(while_block, LANG_JAVA)
        self.assertEqual(2, len(blocks))

    def test_identify_unique_block_with_sync(self) -> None:
        sync_block = '''
        synchronized (getLock(cache)) {
           url = cache.toURI().toURL();
        }'''
        blocks, _ = determine_unique_blocks(sync_block, LANG_JAVA)
        self.assertEqual(2, len(blocks))

    def test_identify_unique_block_with_for(self) -> None:
        for_cycle_block = '''
        for (int i = 0; i < 10; ++i) {
            foo();
        }'''
        blocks, _ = determine_unique_blocks(for_cycle_block, LANG_JAVA)
        self.assertEqual(2, len(blocks))

    def test_identify_unique_block_without_brackets(self) -> None:
        block_without_brackets = '''
        for (int i = 0; i < 10; ++i)
            foo();
        '''
        blocks, _ = determine_unique_blocks(block_without_brackets, LANG_JAVA)
        self.assertEqual(2, len(blocks))

    def test_identify_unique_blocks_with_try(self) -> None:
        block_without_try = '''
            try {
                tracker.waitForAll();
            } catch (Exception e) {
                int i = 0;
            }
            finally {
                int j = 0;
            }
        '''
        blocks, _ = determine_unique_blocks(block_without_try, LANG_JAVA)
        self.assertEqual(4, len(blocks))

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
        blocks, _ = determine_unique_blocks(block_without_try, LANG_JAVA)
        self.assertEqual(3, len(blocks))

    def test_identify_unique_blocks_with_lambda(self) -> None:
        block_without_lambda = '''
            MyPrinter myPrinter = (s) -> { System.out.println(s); };
        '''
        blocks, _ = determine_unique_blocks(block_without_lambda, LANG_JAVA)
        self.assertEqual(2, len(blocks))

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
        blocks, _ = determine_unique_blocks(while_block, LANG_JAVA)
        self.assertEqual(2, len(blocks))

    def test_identify_unique_block_with_continue(self) -> None:
        while_block = '''
        for (String s: strings) {
             a();
             b();
             if (true) { continue;}
        }
        '''
        blocks, _ = determine_unique_blocks(while_block, LANG_JAVA)
        self.assertEqual(1, len(blocks))

    def test_opportunities_ranges(self):
        expected_opportunities = [
            ((1, 8), (1, 19)), ((1, 8), (2, 38)), ((1, 8), (3, 53)), ((1, 8), (14, 9)), ((1, 8), (28, 9)),
            ((1, 8), (29, 59)), ((1, 8), (39, 10)), ((1, 8), (41, 51)), ((1, 8), (43, 34)), ((1, 8), (46, 34)),
            ((1, 8), (47, 17)), ((2, 8), (2, 38)), ((2, 8), (3, 53)), ((2, 8), (14, 9)), ((2, 8), (28, 9)),
            ((2, 8), (29, 59)), ((2, 8), (39, 10)), ((2, 8), (41, 51)), ((2, 8), (43, 34)), ((2, 8), (46, 34)),
            ((2, 8), (47, 17)), ((3, 8), (3, 53)), ((3, 8), (14, 9)), ((3, 8), (28, 9)), ((3, 8), (29, 59)),
            ((3, 8), (39, 10)), ((3, 8), (41, 51)), ((3, 8), (43, 34)), ((3, 8), (46, 34)), ((3, 8), (47, 17)),
            ((5, 8), (14, 9)), ((5, 8), (28, 9)), ((5, 8), (29, 59)), ((5, 8), (39, 10)), ((5, 8), (41, 51)),
            ((5, 8), (43, 34)), ((5, 8), (46, 34)), ((5, 8), (47, 17)), ((6, 12), (6, 33)), ((6, 12), (7, 34)),
            ((7, 12), (7, 34)), ((9, 12), (9, 22)), ((9, 12), (10, 16)), ((10, 12), (10, 16)), ((12, 12), (12, 22)),
            ((12, 12), (13, 16)), ((13, 12), (13, 16)), ((16, 8), (28, 9)), ((16, 8), (29, 59)), ((16, 8), (39, 10)),
            ((16, 8), (41, 51)), ((16, 8), (43, 34)), ((16, 8), (46, 34)), ((16, 8), (47, 17)), ((17, 12), (17, 18)),
            ((17, 12), (26, 13)), ((18, 12), (26, 13)), ((19, 16), (25, 17)), ((20, 20), (20, 42)),
            ((20, 20), (21, 42)), ((21, 20), (21, 42)), ((24, 20), (24, 42)), ((29, 8), (29, 59)),
            ((29, 8), (39, 10)), ((29, 8), (41, 51)), ((29, 8), (43, 34)),
            ((29, 8), (46, 34)), ((29, 8), (47, 17)), ((31, 8), (39, 10)), ((31, 8), (41, 51)), ((31, 8), (43, 34)),
            ((31, 8), (46, 34)), ((31, 8), (47, 17)), ((33, 16), (33, 46)), ((36, 16), (36, 31)), ((36, 16), (37, 52)),
            ((37, 16), (37, 52)), ((41, 8), (41, 51)), ((41, 8), (43, 34)), ((41, 8), (46, 34)), ((41, 8), (47, 17)),
            ((42, 8), (43, 34)), ((42, 8), (46, 34)), ((42, 8), (47, 17)), ((43, 12), (43, 33)), ((45, 8), (46, 34)),
            ((45, 8), (47, 17)), ((46, 12), (46, 33)), ((47, 8), (47, 17))
        ]
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
        found_opportunities = get_block_slices(self.t_, LANG_JAVA, min_range=1, max_percentage=1.00)
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
        found_opportunities = {(x[0][0], x[1][0]) for x in get_block_slices(
            code,
            LANG_JAVA,
            min_range=1,
            max_percentage=1.00)}
        self.assertTrue((12, 12) in found_opportunities, True)
        self.assertTrue((15, 15) in found_opportunities, True)
        self.assertTrue((21, 21) in found_opportunities, True)
        self.assertTrue((23, 23) in found_opportunities, True)

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
        found_opportunities = {(x[0][0], x[1][0]) for x in get_block_slices(
            code,
            LANG_JAVA,
            min_range=3,
            max_percentage=0.8)}
        self.assertTrue([x for x in found_opportunities if x[1][0] - x[0][0] <= 3], 0)
        self.assertTrue([x for x in found_opportunities if len(all_lines) / (x[1][0] - x[0][0]) > max_percentage], 0)

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
        found_opportunities = {(x[0][0], x[1][0]) for x in get_block_slices(
            code,
            LANG_JAVA,
            min_range=2,
            max_percentage=1.00)}
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
        found_opportunities = {(x[0][0], x[1][0]) for x in get_block_slices(
            code_with_usage_inside_inner_scope,
            LANG_JAVA,
            min_range=2,
            max_percentage=1.00)}
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
        found_opportunities = {(x[0][0], x[1][0]) for x in get_block_slices(
            complex_objects,
            LANG_JAVA,
            min_range=0,
            max_percentage=1.00)}

        self.assertTrue((3, 4) in found_opportunities, True)
        self.assertTrue((3, 5) in found_opportunities, True)
        self.assertTrue((3, 6) in found_opportunities, True)
        self.assertTrue((3, 7) in found_opportunities, True)
        self.assertTrue((4, 5) in found_opportunities, True)
        self.assertTrue((4, 6) in found_opportunities, True)
        self.assertTrue((4, 7) in found_opportunities, True)

    def test_do_not_filter_with_diff_scope(self):
        diff_scope = '''
            Object h = new Object();
            for(int i = 0; i < 5; ++i) {
                {
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
        found_opportunities = {(x[0][0], x[1][0]) for x in get_block_slices(
            diff_scope,
            LANG_JAVA,
            min_range=0,
            max_percentage=1.00)}
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
        found_opportunities = {(x[0][0], x[1][0]) for x in get_block_slices(
            diff_scope,
            LANG_JAVA,
            min_range=1,
            max_percentage=1.00)}
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
        found_opportunities = {(x[0][0], x[1][0]) for x in get_block_slices(
            diff_scope,
            LANG_JAVA,
            min_range=1,
            max_percentage=1.00)}
        self.assertTrue((3, 4) not in found_opportunities)
        self.assertTrue((3, 5) not in found_opportunities)
        self.assertTrue((3, 6) not in found_opportunities)
        self.assertTrue((3, 7) not in found_opportunities)

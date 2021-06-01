__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2021/03/22'

from unittest import TestCase

from program_slicing.decomposition import slicing
from program_slicing.decomposition.block_slicing import determine_unique_blocks, get_opportunities_list

is_slicing_criterion = slicing.__is_slicing_criterion
obtain_variable_statements = slicing.__obtain_variable_statements
obtain_seed_statements = slicing.__obtain_seed_statements
obtain_slicing_criteria = slicing.__obtain_slicing_criteria
obtain_common_boundary_blocks = slicing.__obtain_common_boundary_blocks


class SlicingTestCase(TestCase):

    def test_identify_unique_block_with_if(self):
        if_statement = '''
        if (workspace == null) {
            return Collections.emptySet();
        }
        '''
        blocks = determine_unique_blocks(if_statement)
        self.assertEqual(len(blocks), 2)

    def test_identify_unique_block_with_for_each(self):
        for_each_block = '''
        for (LaunchConfiguration config: workspace.getLaunchConfigurations()) { int i = 0;}
        '''
        blocks = determine_unique_blocks(for_each_block)
        self.assertEqual(len(blocks), 2)

    def test_identify_unique_block_with_while(self):
        while_block = '''
        while (null != (line = input.readLine()) && maxLines > 0) {
                maxLines--;
        }'''
        blocks = determine_unique_blocks(while_block)
        self.assertEqual(len(blocks), 2)

    def test_identify_unique_block_with_sync(self):
        sync_block = '''
        synchronized (getLock(cache)) {
           url = cache.toURI().toURL();
        }'''
        blocks = determine_unique_blocks(sync_block)
        self.assertEqual(len(blocks), 2)

    def test_identify_unique_block_with_for(self):
        for_cycle_block = '''
        for (int i = 0; i < 10; ++i) {
            foo();
        }'''
        blocks = determine_unique_blocks(for_cycle_block)
        self.assertEqual(len(blocks), 2)

    def test_identify_unique_block_without_brackets(self):
        block_without_brackets = '''
        for (int i = 0; i < 10; ++i)
            foo();
        '''
        blocks = determine_unique_blocks(block_without_brackets)
        self.assertEqual(len(blocks), 2)

    def test_identify_unique_blocks_with_try(self):
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
        blocks = determine_unique_blocks(block_without_try)
        self.assertEqual(len(blocks), 4)

    def test_identify_unique_blocks_with_anonymous_classn(self):
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
        blocks = determine_unique_blocks(block_without_try)
        self.assertEqual(len(blocks), 3)

    def test_identify_unique_blocks_with_lambda(self):
        block_without_lambda = '''
            MyPrinter myPrinter = (s) -> { System.out.println(s); };
        '''
        blocks = determine_unique_blocks(block_without_lambda)
        self.assertEqual(len(blocks), 2)

    def test_opportunities_ranges(self):
        code = '''
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
            ((20, 20), (21, 42)),
            ((21, 20), (21, 42)), ((29, 8), (29, 59)), ((29, 8), (39, 10)), ((29, 8), (41, 51)), ((29, 8), (43, 34)),
            ((29, 8), (46, 34)), ((29, 8), (47, 17)), ((31, 8), (39, 10)), ((31, 8), (41, 51)), ((31, 8), (43, 34)),
            ((31, 8), (46, 34)), ((31, 8), (47, 17)), ((33, 16), (33, 46)), ((36, 16), (36, 31)), ((36, 16), (37, 52)),
            ((37, 16), (37, 52)), ((41, 8), (41, 51)), ((41, 8), (43, 34)), ((41, 8), (46, 34)), ((41, 8), (47, 17)),
            ((42, 8), (43, 34)), ((42, 8), (46, 34)), ((42, 8), (47, 17)), ((43, 12), (43, 33)), ((45, 8), (46, 34)),
            ((45, 8), (47, 17)), ((46, 12), (46, 33)), ((47, 8), (47, 17))]
        found_opportunities = get_opportunities_list(code)
        self.assertEqual(expected_opportunities, found_opportunities)

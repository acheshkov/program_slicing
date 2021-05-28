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
        self.assertEqual(len(blocks), 4)

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
            [(2, 2), (2, 3), (2, 4), (2, 15), (2, 29), (2, 30), (2, 40), (2, 42), (2, 44), (2, 47), (2, 48),
             (3, 3), (3, 4), (3, 15), (3, 29), (3, 30), (3, 40), (3, 42), (3, 44), (3, 47), (3, 48),
             (4, 4), (4, 15), (4, 29), (4, 30), (4, 40), (4, 42), (4, 44), (4, 47), (4, 48),
             (6, 15), (6, 29), (6, 30), (6, 40), (6, 42), (6, 44), (6, 47), (6, 48),
             (7, 7), (7, 8),
             (8, 8),
             (10, 10), (10, 11),
             (11, 11),
             (13, 13), (13, 14), (14, 14),
             (17, 29), (17, 30), (17, 40), (17, 42), (17, 44), (17, 47), (17, 48),
             (18, 18), (18, 27),
             (19, 27),
             (20, 26),
             (21, 21), (21, 22),
             (22, 22),
             (30, 30), (30, 40), (30, 42), (30, 44), (30, 47), (30, 48),
             (32, 40), (32, 42), (32, 44), (32, 47), (32, 48),
             (34, 34),
             (37, 37), (37, 38),
             (38, 38),
             (42, 42), (42, 44), (42, 47), (42, 48),
             (43, 44), (43, 47), (43, 48),
             (44, 44),
             (46, 47), (46, 48),
             (47, 47),
             (48, 48)]
        ]
        found_opportunities = get_opportunities_list(code)
        self.assertEqual(expected_opportunities, found_opportunities)
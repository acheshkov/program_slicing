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

    def test_get_blocks(self):
        if_statement = '''
        if (workspace == null) {
            return Collections.emptySet();
        }
        '''
        blocks = determine_unique_blocks(if_statement)
        self.assertEqual(len(blocks), 2)

        for_each_block = '''
        for (LaunchConfiguration config: workspace.getLaunchConfigurations()) { int i = 0;}
        '''
        blocks = determine_unique_blocks(for_each_block)
        self.assertEqual(len(blocks), 2)

        while_block = '''
        while (null != (line = input.readLine()) && maxLines > 0) {
                maxLines--;
        }'''
        blocks = determine_unique_blocks(while_block)
        self.assertEqual(len(blocks), 2)

        sync_block = '''
        synchronized (getLock(cache)) {
           url = cache.toURI().toURL();
        }'''
        blocks = determine_unique_blocks(sync_block)
        self.assertEqual(len(blocks), 2)

        for_cycle_block = '''
        for (int i = 0; i < 10; ++i) {
            foo();
        }'''
        blocks = determine_unique_blocks(for_cycle_block)
        self.assertEqual(len(blocks), 2)

        block_without_brackets = '''
        for (int i = 0; i < 10; ++i)
            foo();
        '''
        blocks = determine_unique_blocks(block_without_brackets)
        self.assertEqual(len(blocks), 2)

    def test_get_all_opportunities(self):
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
            ArrayList<String> strs = new ArrayList<>();
            for (String s: strs)
                System.out.println(s);

            while(b < 10)
                System.out.println(s);
            return t;'''

        opportunities = [
            (1, 1), (1, 2), (1, 3), (1, 11), (1, 25), (1, 26), (1, 28), (1, 31), (1, 32),
            (2, 2), (2, 3), (2, 11), (2, 25), (2, 26), (2, 28), (2, 31), (2, 32),
            (3, 3), (3, 11), (3, 25), (3, 26), (3, 28), (3, 31), (3, 32),
            (5, 11), (5, 25), (5, 26), (5, 28), (5, 31), (5, 32),
            (6, 6), (6, 7),
            (7, 7),
            (9, 9), (9, 10),
            (10, 10),
            (13, 25), (13, 26), (13, 28), (13, 31), (13, 32),
            (14, 14), (14, 23),
            (15, 23),
            (16, 22),
            (17, 17), (17, 18),
            (18, 18),
            (26, 26), (26, 28), (26, 31), (26, 32),
            (27, 28), (27, 31), (27, 32),
            (28, 28),
            (30, 31),
            (30, 32), (31, 31), (32, 32)
        ]

        self.assertEqual(get_opportunities_list(code), opportunities)

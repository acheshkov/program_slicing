import unittest

# from program_slicing.decomposition.expand_slice import expand_slices_ordered


class ExpandSliceTestCase(unittest.TestCase):

    @unittest.skip("not implemented")
    def test_vars_before_1(self):
        """
        output the first 3 minimal expansions from the priority queue
        """
        code_ex = '''public void methodEx(final AClass a) {
                            final int opt = a.getOpt();
                            final int rest = a.getRest();
                            int i = 1;
                            do1(i);
                            if (opt > 0 || rest > -1) {
                                do2(i);
                            }
                        }'''
        slice_to_expand = (5, 7)
        expected_extensions = {[(1, 1), (5, 7)], [(2, 2), (5, 7)], [(1, 2), (5, 7)]}
        extension_generator = expand_slices_ordered(code_ex, slice_to_expand, cost='basic')
        found_extensions = {next(extension_generator) for _ in range(3)}
        self.assertSetEqual(expected_extensions, found_extensions)

    @unittest.skip("not implemented")
    def test_vars_before_2(self):
        """
        output the minimal expansion
        """
        code_ex = '''public void methodEx(final AClass a) {
                    final int opt = a.getOpt();
                    int i = 1;
                    do1(i);
                    if (opt > 0) {
                        LClass optA = a.getOpt();
                        for (int j = 0; j < opt; j++, i++) {
                            System.out.println(optA);
                        }
                    }
                }'''
        slice_to_expand = (6, 8)
        expected_extension_best = [(6, 8)]
        expected_extension_second_best = [(1, 1), (4, 9)]
        extension_generator = expand_slices_ordered(code_ex, slice_to_expand, cost='basic')
        self.assertListEqual(expected_extension_best, next(extension_generator))
        self.assertListEqual(expected_extension_second_best, next(extension_generator))

    @unittest.skip("not implemented")
    def test_expand_invalid_slice_1(self):
        """
        slice not finished in the end
        not including this functionality for now
        """
        code_ex = '''public void methodEx(final AClass a) {
                    if (cond()) {
                        do2(a);
                        do3(a);
                    }
                }'''
        slice_to_expand = (1, 2)
        self.assertRaises(Exception, expand_slices_ordered(code_ex, slice_to_expand))

    @unittest.skip("not implemented")
    def test_expand_invalid_slice_2(self):
        """
        needs expanding from beginning: 3 expansions of equal cost
        """
        code_ex = '''public void simpleMethod() {
                        int a = 10;
                        for (int i = 0; i < 10 ; i++) {
                            if (i < 4) {
                                do1();
                            } else {
                                a++;
                            }
                            System.out.println(a);
                        }
                    }'''
        slice_to_expand = (6, 8)
        expected_extensions = {[(3, 8)], [(2, 8)], [(1, 8)]}
        extension_generator = expand_slices_ordered(code_ex, slice_to_expand)
        found_extensions = {next(extension_generator) for _ in range(3)}
        self.assertSetEqual(expected_extensions, found_extensions)

    @unittest.skip("not implemented")
    def test_vars_after(self):
        """
        output first 3 minimal expansions from the priority queue
        (they reduce the number of IN)
        """
        code_ex_after = '''public void methodEx(boolean a){
                            RClass r = getR();
                            if (a) {
                                r.update();
                            }
                            System.out.println('Message');
                            do1(r);
                            do2(a);
                        }'''
        slice_to_expand = (1, 4)
        expected_extensions = {[(1, 4)], [(1, 4), (5, 5)]}
        extension_generator = expand_slices_ordered(code_ex_after, slice_to_expand, cost='basic')
        found_extensions = {next(extension_generator) for _ in range(2)}
        self.assertSetEqual(expected_extensions, found_extensions)

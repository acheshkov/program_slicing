import unittest

# from program_slicing.decomposition.expand_slice import expand_slices_ordered,\
#                                                        InvalidBlockException


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
        slice_to_expand = (6, 8)
        expected_extensions = {[2], [3], [2, 3]}
        extension_generator = expand_slices_ordered(code_ex, slice_to_expand)
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
        slice_to_expand = (7, 9)
        expected_extension = [6]
        extension_generator = expand_slices_ordered(code_ex, slice_to_expand)
        found_extension = next(extension_generator)
        self.assertListEqual(expected_extension, found_extension)

    @unittest.skip("not implemented")
    def test_expand_invalid_slice_1(self):
        """
        slice not finished in the end
        """
        code_ex = '''public void methodEx(final AClass a) {
                    if (cond()) {
                        do2(a);
                        do3(a);
                    }
                }'''
        slice_to_expand = (2, 3)
        self.assertRaises(InvalidBlockException, expand_slices_ordered(code_ex, slice_to_expand))

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
        slice_to_expand = (7, 9)
        expected_extensions = {[4, 5, 6], [3, 4, 5, 6], [2, 3, 4, 5, 6]}
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
        slice_to_expand = (2, 4)
        expected_extension = [6]
        extension_generator = expand_slices_ordered(code_ex_after, slice_to_expand)
        found_extension = next(extension_generator)
        self.assertSetEqual(expected_extension, found_extension)

    @unittest.skip("not implemented")
    def test_multiple_vars(self):
        """
        expansion wrt var a and both a and b have equal cost,
        even though b is not used in the slice
        """
        code_ex_multiple_vars = '''public void method() {
                                    int a = 1;
                                    int b = 2;
                                    inv1(a, b);
                                    inv2(a);
                                }'''
        slice_to_expand = (5, 5)
        expected_extensions = {[2, 4], [2, 3, 4]}
        extension_generator = expand_slices_ordered(code_ex_multiple_vars, slice_to_expand)
        extension_generator = expand_slices_ordered(code_ex_multiple_vars, slice_to_expand)
        found_extensions = {next(extension_generator) for _ in range(3)}
        self.assertSetEqual(expected_extensions, found_extensions)

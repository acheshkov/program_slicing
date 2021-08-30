import unittest

# from program_slicing.decomposition.expand_slice import expand_slices_ordered


class ExpandSliceTestCase(unittest.TestCase):

    code_ex_before = '''public Operand receiveA(final AClass a, Scope s) {
                            final int required = a.getRequired();
                            final int opt = a.getOpt();
                            final int rest = a.getRest();
                                
                            int index = 1;
                            
                            LClass pre = a.getPre();
                            for (int i = 0; i < required; i++, index++) {
                                if (condition()) {
                                    do1(pre, index);
                                }
                            }
                    
                            if (opt > 0 || rest > -1) {
                                LClass optA = a.getOpt();
                                for (int j = 0; j < opt; j++, index++) {
                                    s.addInstr(new Instr(optA), index));
                                    System.out.println(optA);
                                }
                    
                                if (rest > -1) {
                                    s.addInstr(new Instr(new LocVar(a.getAN()), index));
                                    index++;
                                }
                            }
                        }'''

    @unittest.skip("not implemented")
    def test_vars_before_1(self):
        """
        output the first 3 minimal expansions from the priority queue
        """
        slice_to_expand = (15, 26)
        expected_extensions = {[3], [4], [3, 4]}
        extension_generator = expand_slices_ordered(self.code_ex_before, slice_to_expand)
        found_extensions = {next(extension_generator) for _ in range(3)}
        self.assertSetEqual(expected_extensions, found_extensions)

    @unittest.skip("not implemented")
    def test_vars_before_2(self):
        """
        output the minimal expansion
        """
        slice_to_expand = (17, 20)
        expected_extension = [16]
        extension_generator = expand_slices_ordered(self.code_ex_before, slice_to_expand)
        found_extension = next(extension_generator)
        self.assertListEqual(expected_extension, found_extension)

    @unittest.skip("not implemented")
    def test_expand_invalid_slice_1(self):
        """
        slice not finished in the end
        """
        slice_to_expand = (17, 18)
        expected_extension = [19]
        extension_generator = expand_slices_ordered(self.code_ex_before, slice_to_expand)
        found_extension = next(extension_generator)
        self.assertListEqual(expected_extension, found_extension)

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
        code_ex_after = '''public void entry(EClass entry, boolean r, long duration){
                                RClass rospl = getRospl();
                                if (r) {
                                    if (cond()) {
                                        String s;
                                        if (cond2()) {
                                            s = "for " + duration;
                                        } else {
                                            s = "indefinitely";
                                        }
                                    }
                                    entry.update(duration);
                                } else {
                                    rospl.dropEntry();
                                }
                                System.out.println('Message');
                                notifyWaitingThread(rospl);
                                someCommand(r);
                            }'''
        slice_to_expand = (2, 15)
        expected_extensions = {[17], [18], [17, 18]}
        extension_generator = expand_slices_ordered(code_ex_after, slice_to_expand)
        found_extensions = {next(extension_generator) for _ in range(3)}
        self.assertSetEqual(expected_extensions, found_extensions)

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

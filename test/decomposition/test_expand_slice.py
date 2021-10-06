__licence__ = 'MIT'
__author__ = 'KatGarmash'
__credits__ = ['KatGarmash']
__maintainer__ = 'KatGarmash'
__date__ = '2021/09/14'


import unittest

from program_slicing.decomposition import extended_blocks
from program_slicing.decomposition.extended_blocks import get_block_extensions,
from program_slicing.decomposition.program_slice import ProgramSlice
from program_slicing.graph.manager import ProgramGraphsManager
from program_slicing.graph.parse import Lang
from program_slicing.graph.point import Point

get_incoming_variables = extended_blocks.__get_incoming_variables
get_outgoing_variables = extended_blocks.__get_outgoing_variables
extend_block_singleton = extended_blocks.__extend_block_singleton
filter_anti_dependence = extended_blocks.__filter_anti_dependence
filter_more_than_one_outgoing = extended_blocks.__filter_more_than_one_outgoing
filter_control_dependence = extended_blocks.__filter_control_dependence


class ExpandSliceTestCase(unittest.TestCase):

    @unittest.skip("not implemented")
    def test_vars_before_1(self) -> None:
        """
        Output the first 3 minimal expansions from the priority queue.
        """
        code_ex = """
        public void methodEx(final AClass a) {
            final int opt = a.getOpt();
            final int rest = a.getRest();
            int i = 1;
            do1(i);
            if (opt > 0 || rest > -1) {
                do2(i);
            }
        }"""
        slice_to_expand = (6, 8)
        expected_extensions = {[2], [3], [2, 3]}
        extension_generator = expand_slices_ordered(code_ex, slice_to_expand)
        found_extensions = {next(extension_generator) for _ in range(3)}
        self.assertEqual(expected_extensions, found_extensions)

    @unittest.skip("not implemented")
    def test_vars_before_2(self):
        """
        output the minimal expansion
        """
        code_ex = """
        public void methodEx(final AClass a) {
            final int opt = a.getOpt();
            int i = 1;
            do1(i);
            if (opt > 0) {
                LClass optA = a.getOpt();
                for (int j = 0; j < opt; j++, i++) {
                    System.out.println(optA);
                }
            }
        }"""
        slice_to_expand = (7, 9)
        expected_extension = [6]
        extension_generator = expand_slices_ordered(code_ex, slice_to_expand)
        found_extension = next(extension_generator)
        self.assertEqual(expected_extension, found_extension)

    @unittest.skip("not implemented")
    def test_expand_invalid_slice_1(self):
        """
        slice not finished in the end
        not including this functionality for now
        """
        code_ex = """
        public void methodEx(final AClass a) {
            if (cond()) {
                do2(a);
                do3(a);
            }
        }"""
        slice_to_expand = (2, 3)
        self.assertRaises(Exception, expand_slices_ordered(code_ex, slice_to_expand))

    @unittest.skip("not implemented")
    def test_expand_invalid_slice_2(self):
        """
        needs expanding from beginning: 3 expansions of equal cost
        """
        code_ex = """
        public void simpleMethod() {
            int a = 10;
            for (int i = 0; i < 10 ; i++) {
                if (i < 4) {
                    do1();
                } else {
                    a++;
                }
                System.out.println(a);
            }
        }"""
        slice_to_expand = (7, 9)
        expected_extensions = {[4, 5, 6], [3, 4, 5, 6], [2, 3, 4, 5, 6]}
        extension_generator = expand_slices_ordered(code_ex, slice_to_expand)
        found_extensions = {next(extension_generator) for _ in range(3)}
        self.assertEqual(expected_extensions, found_extensions)

    @unittest.skip("not implemented")
    def test_vars_after(self):
        """
        output first 3 minimal expansions from the priority queue
        (they reduce the number of IN)
        """
        code_ex_after = """
        public void methodEx(boolean a){
            RClass r = getR();
            if (a) {
                r.update();
            }
            System.out.println('Message');
            do1(r);
            do2(a);
        }"""
        slice_to_expand = (2, 4)
        expected_extension = [6]
        extension_generator = expand_slices_ordered(code_ex_after, slice_to_expand)
        found_extension = next(extension_generator)
        self.assertEqual(expected_extension, found_extension)

    @unittest.skip("not implemented")
    def test_multiple_vars(self):
        """
        expansion wrt var a and both a and b have equal cost,
        even though b is not used in the slice
        """
        code_ex_multiple_vars = """
        public void method() {
            int a = 1;
            int b = 2;
            inv1(a, b);
            inv2(a);
        }"""
        slice_to_expand = (5, 5)
        expected_extensions = {[2, 4], [2, 3, 4]}
        extension_generator = expand_slices_ordered(code_ex_multiple_vars, slice_to_expand)
        extension_generator = expand_slices_ordered(code_ex_multiple_vars, slice_to_expand)
        found_extensions = {next(extension_generator) for _ in range(3)}
        self.assertEqual(expected_extensions, found_extensions)

    def test_get_incoming_variables_1(self):
        code_1 = """
        public void methodEx(final AClass a) {
            final int opt = a.getOpt();
            final int rest = a.getRest();
            int i = 1;
            if (opt > 0 || rest > -1) {
                do2(i);
            }
        }"""
        manager = ProgramGraphsManager(code_1, Lang.JAVA)
        block_11 = manager.get_statements_in_range(Point(5, 0), Point(7, 10000))
        incoming_variables_11 = get_incoming_variables(block_11, manager)
        self.assertEqual(set(incoming_variables_11.keys()), {'opt', 'rest', 'i'})

    def test_get_incoming_variables_2(self):
        code = """
        public void methodEx() {
            int i = 1;
            do1(i);
            i = 2;
            do2(i);
        }"""
        manager = ProgramGraphsManager(code, Lang.JAVA)
        block = manager.get_statements_in_range(Point(4, 0), Point(5, 10000))
        incoming_variables = get_incoming_variables(block, manager)
        self.assertEqual(set(incoming_variables.keys()), set())

    def test_get_incoming_variables_3(self):
        code = """
        public void methodEx(final AClass a) {
            final int opt = a.getOpt();
            int i = 1;
            do1(i);
            if (opt > 0) {
                LClass optA = a.getOpt();
                for (int j = 0; j < opt; j++) {
                    System.out.println(optA);
                }
            }
        }"""
        manager = ProgramGraphsManager(code, Lang.JAVA)
        block = manager.get_statements_in_range(Point(7, 0), Point(9, 10000))
        incoming_variables = get_incoming_variables(block, manager)
        self.assertEqual(set(incoming_variables.keys()), {'opt', 'optA'})

    def test_outgoing_variables_1(self):
        code = """
        public void methodEx(boolean a){
            RClass r = getR();
            if (a) {
                r.update();
            }
            System.out.println('Message');
            do1(r);
            do2(a);
        }"""
        manager = ProgramGraphsManager(code, Lang.JAVA)
        block = manager.get_statements_in_range(Point(2, 0), Point(5, 10000))
        outgoing_variables = get_outgoing_variables(block, manager)
        self.assertEqual(set(outgoing_variables.keys()), {'r'})

    def test_outgoing_variables_2(self):
        code = """
        public void methodEx(boolean a){
            RClass r = getR();
            if (a) {
                r.update();
            }
            System.out.println('Message');
            r = updateR();
            do1(r);
            do2(a);
        }"""
        manager = ProgramGraphsManager(code, Lang.JAVA)
        block = manager.get_statements_in_range(Point(2, 0), Point(5, 10000))
        outgoing_variables = get_outgoing_variables(block, manager)
        self.assertEqual(set(outgoing_variables.keys()), set())

    def __compare_extended_slices(self, **kwargs):
        result_extension = kwargs["extension"]
        expected_range = kwargs["expected_range"]
        expected_in = kwargs["expected_in"]
        expected_out = kwargs["expected_out"]

        _range = [(r[0].line_number, r[1].line_number)
                  for r in ProgramSlice(kwargs['source_code']).from_statements(result_extension[0]).ranges]
        in_vars = set(result_extension[1].keys())
        out_vars = set(result_extension[2].keys())
        self.assertEqual(expected_range, _range)
        self.assertEqual(expected_in, in_vars)
        self.assertEqual(expected_out, out_vars)

    def test_extend_block_singleton_1(self):
        code = """
        public void method() {
            int a = 1;
            int b = 2;
            inv1(a, b);
            inv2(a);
        }"""
        manager = ProgramGraphsManager(code, Lang.JAVA)
        block = manager.get_statements_in_range(Point(5, 0), Point(5, 10000))
        singleton_extensions = extend_block_singleton(block, manager)
        name_to_extension = {}
        for ext in singleton_extensions:
            name_to_extension[ext[3]] = ext
        self.assertEqual({'a'}, set(name_to_extension.keys()))

        self.__compare_extended_slices(extension=name_to_extension['a'],
                                       expected_range=[(2, 2), (5, 5)],
                                       expected_in=set(),
                                       expected_out=set(),
                                       source_code=code)

    def test_extend_block_singleton_2(self):
        code = """
        public void methodEx(final AClass a) {
            final int opt = a.getOpt();
            final int rest = a.getRest();
            int i = 1;
            do1(i);
            if (opt > 0 || rest > -1) {
                do2(i);
            }
        }"""
        manager = ProgramGraphsManager(code, Lang.JAVA)

        block = manager.get_statements_in_range(Point(6, 0), Point(8, 10000))
        singleton_extensions = extend_block_singleton(block, manager)
        name_to_extension = {}
        for ext in singleton_extensions:
            name_to_extension[ext[3]] = ext
        self.assertEqual({'opt', 'rest', 'i'}, set(name_to_extension.keys()))

        self.__compare_extended_slices(extension=name_to_extension['opt'],
                                       expected_range=[(2, 2), (6, 6), (7, 7), (8, 8)],
                                       expected_in={'rest', 'i'},
                                       expected_out=set(),
                                       source_code=code
                                       )

        self.__compare_extended_slices(extension=name_to_extension['rest'],
                                       expected_range=[(3, 3), (6, 6), (7, 7), (8, 8)],
                                       expected_in={'opt', 'i'},
                                       expected_out=set(),
                                       source_code=code
                                       )

        self.__compare_extended_slices(extension=name_to_extension['i'],
                                       expected_range=[(4, 4), (6, 6), (7, 7), (8, 8)],
                                       expected_in={'opt', 'rest'},
                                       expected_out=set(),
                                       source_code=code
                                       )

    def test_extend_block_singleton_3(self):
        code = """
        public void methodEx(){
            RClass r = getR();
            if (cond()) {
                r.update();
            }
            System.out.println('Message');
            do1(r);
            do2(a);
        }"""
        manager = ProgramGraphsManager(code, Lang.JAVA)
        block = manager.get_statements_in_range(Point(2, 0), Point(5, 10000))
        singleton_extensions = extend_block_singleton(block, manager)
        name_to_extension = {}
        for ext in singleton_extensions:
            name_to_extension[ext[3]] = ext
        self.assertEqual({'r'}, set(name_to_extension.keys()))

        self.__compare_extended_slices(extension=name_to_extension['r'],
                                       expected_range=[(2, 2), (3, 3), (4, 4), (5, 5), (7, 7)],
                                       expected_in=set(),
                                       expected_out=set(),
                                       source_code=code
                                       )

    @unittest.skip("need to fix bug in parser")
    def test_extend_block_singleton_4(self):
        code = """
        public void methodEx(boolean a){
            System.out.println();
            if (cond(a)) {
                bla();
            }
        }"""
        manager = ProgramGraphsManager(code, Lang.JAVA)
        block = manager.get_statements_in_range(Point(3, 0), Point(4, 10000))
        singleton_extensions = extend_block_singleton(block, manager)
        name_to_extension = {}
        for ext in singleton_extensions:
            name_to_extension[ext[3]] = ext
        self.assertEqual({''}, set(name_to_extension.keys()))

        self.__compare_extended_slices(extension=name_to_extension[''],
                                       expected_range=[(2, 2), (3, 3), (4, 4), (5, 5)],
                                       expected_in={'a'},
                                       expected_out=set(),
                                       source_code=code
                                       )

    def test_filter_anti_dependence_negative(self):
        """
        extended slice [(1, 1), (3,3)] -- we should filter such examples
        """
        code = """
        public void methodEx() {
            int a = 1;
            do1(a);
            do2(a);
        }"""
        manager = ProgramGraphsManager(code, Lang.JAVA)
        block = manager.get_statements_in_range(Point(4, 0), Point(4, 10000))
        extension = manager.get_statements_in_range(Point(2, 0), Point(2, 10000))
        self.assertFalse(filter_anti_dependence(extension.difference(block), block, manager))

    def test_filter_anti_dependence_positive(self):
        """
        extended slice [(1,3)] from (2,2) -- this one does not violate
        """
        code = """
        public void methodEx() {
            int a = 1;
            do1(a);
            do2(a);
        }"""
        manager = ProgramGraphsManager(code, Lang.JAVA)
        block = manager.get_statements_in_range(Point(3, 0), Point(3, 10000))
        extension_1 = manager.get_statements_in_range(Point(2, 0), Point(2, 10000))
        extension_2 = manager.get_statements_in_range(Point(4, 0), Point(4, 10000))
        self.assertTrue(
            filter_anti_dependence((extension_1.union(extension_2)).difference(block), block, manager))

    def test_filter_more_than_one_outgoing_negative_1(self):
        code = """
        public void methodEx() {
            int i = 1;
            int b = 2;
            do1(i, b);
            do1(b);
        }"""
        manager = ProgramGraphsManager(code, Lang.JAVA)
        slice_candidate = manager.get_statements_in_range(Point(2, 0), Point(3, 10000))
        self.assertFalse(filter_more_than_one_outgoing(slice_candidate, manager))

    def test_filter_more_than_one_outgoing_negative_2(self):
        code = """
        public void methodEx() {
            int i = 1;
            int b = 2;
            i = b + 2;
            do1(i, b);
            do1(b);
        }"""
        manager = ProgramGraphsManager(code, Lang.JAVA)
        slice_candidate = manager.get_statements_in_range(Point(3, 0), Point(4, 10000))
        self.assertFalse(filter_more_than_one_outgoing(slice_candidate, manager))

    def test_filter_more_than_one_outgoing_positive(self):
        code = """
        public void methodEx() {
            int i = 1;
            int b = 2;
            i = b + 2;
        }"""
        manager = ProgramGraphsManager(code, Lang.JAVA)
        slice_candidate = manager.get_statements_in_range(Point(3, 0), Point(4, 10000))
        self.assertTrue(filter_more_than_one_outgoing(slice_candidate, manager))

    @unittest.skip('bug in ProgramManager')
    def test_filter_control_dependence_negative_1(self):
        code = """
        public void methodEx() {
            int a = 1;
            for (int i=1; i < 10 ; i++) {
                System.out.println('Something');
                do1(a);
        }"""
        manager = ProgramGraphsManager(code, Lang.JAVA)
        block = manager.get_statements_in_range(Point(5, 0), Point(5, 10000))
        extension_1 = manager.get_statements_in_range(Point(2, 0), Point(3, 10000))
        extension_2 = manager.get_statements_in_range(Point(6, 0), Point(6, 10000))
        self.assertFalse(filter_control_dependence(extension_1.union(extension_2), block, manager))

    @unittest.skip('bug in ProgramManager')
    def test_filter_control_dependence_negative_2(self):
        code = """
        public void methodEx() {
            int a = 1;
            for (int i=1; i < 10 ; i++) {
                System.out.println('Something');
                do1(a);
            }
        }"""
        manager = ProgramGraphsManager(code, Lang.JAVA)
        block = manager.get_statements_in_range(Point(2, 0), Point(2, 10000))
        extension = manager.get_statements_in_range(Point(5, 0), Point(5, 10000))
        self.assertFalse(filter_control_dependence(extension, block, manager))

    @unittest.skip('bug in ProgramManager')
    def test_filter_control_dependence_positive_1(self):
        code = """
        public void methodEx() {
            int a = 1;
            for (int i=1; i < 10 ; i++) {
                System.out.println('Something');
                do1(a);
            }
        }"""
        manager = ProgramGraphsManager(code, Lang.JAVA)
        block = manager.get_statements_in_range(Point(4, 0), Point(5, 10000))
        extension = manager.get_statements_in_range(Point(2, 0), Point(3, 10000))
        self.assertTrue(filter_control_dependence(extension, block, manager))

    def test_get_block_extensions_1(self):
        code_ex = """
        public void methodEx(final AClass a) {
            final int opt = a.getOpt();
            final int rest = a.getRest();
            int i = 1;
            do1(i);
            if (opt > 0 || rest > -1) {
                do2(i);
            }
        }"""
        manager = ProgramGraphsManager(code_ex, Lang.JAVA)
        block = manager.get_statements_in_range(Point(6, 0), Point(8, 10000))
        result_extension_ranges = []
        for ext in get_block_extensions(block, manager, code_ex.split("\n")):
            _range = [(r[0].line_number, r[1].line_number) for r in ext.ranges]
            result_extension_ranges.append(_range)
        expected_extension_ranges = [[(6, 6), (7, 7), (8, 8)],
                                     [(2, 2), (6, 6), (7, 7), (8, 8)],
                                     [(3, 3), (6, 6), (7, 7), (8, 8)],
                                     [(2, 2), (3, 3), (6, 6), (7, 7), (8, 8)]]

        self.assertEqual(sorted(expected_extension_ranges),
                         sorted(result_extension_ranges))

    def test_get_block_extensions_2(self):
        code_ex = """
        public void methodEx(final AClass a) {
            final int opt = a.getOpt();
            int i = 1;
            do1(i);
            if (opt > 0) {
                for (int j = 0; j < opt; j++, i++) {
                    System.out.println(opt);
                }
            }
        }"""
        manager = ProgramGraphsManager(code_ex, Lang.JAVA)
        block = manager.get_statements_in_range(Point(6, 0), Point(8, 10000))
        result_extension_ranges = []
        for ext in get_block_extensions(block, manager, code_ex.split("\n")):
            _range = [(r[0].line_number, r[1].line_number) for r in ext.ranges]
            result_extension_ranges.append(_range)
        expected_extension_ranges = [
            [(6, 6), (7, 7), (8, 8)],
            [(2, 2), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9)]]

        self.assertEqual(sorted(expected_extension_ranges), sorted(result_extension_ranges))

    def test_get_block_extensions_3(self):
        code_ex = """
        public void methodEx(final AClass a) {
            int e = 1;
            do1(e);
            if (cond()) {
                LClass optA = a.getOpt();
                System.out.println(optA, e);
            }
        }"""
        manager = ProgramGraphsManager(code_ex, Lang.JAVA)
        block = manager.get_statements_in_range(Point(6, 0), Point(6, 10000))
        result_extension_ranges = []
        for ext in get_block_extensions(block, manager, code_ex.split("\n")):
            _range = [(r[0].line_number, r[1].line_number) for r in ext.ranges]
            result_extension_ranges.append(_range)
        expected_extension_ranges = [[(6, 6)],
                                     [(4, 4), (5, 5), (6, 6), (7, 7)]]

        self.assertEqual(sorted(expected_extension_ranges),
                         sorted(result_extension_ranges))

    def test_get_block_extensions_4(self):
        code_ex = """
        public void methodEx(final AClass a) {
            final int opt = a.getOpt();
            int i = 1;
            do1(i);
            if (opt > 0) {
                LClass optA = a.getOpt();
                for (int j = 0; j < opt; j++, i++) {
                    System.out.println(optA);
                }
            }
        }"""
        manager = ProgramGraphsManager(code_ex, Lang.JAVA)
        block = manager.get_statements_in_range(Point(7, 0), Point(9, 10000))
        result_extension_ranges = []
        for ext in get_block_extensions(block, manager, code_ex.split("\n")):
            _range = [(r[0].line_number, r[1].line_number)
                      for r in ext.ranges]
            result_extension_ranges.append(_range)
        expected_extension_ranges = [[(7, 7), (8, 8), (9, 9)],
                                     [(2, 2), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10)]]

        self.assertEqual(sorted(expected_extension_ranges),
                         sorted(result_extension_ranges))

    def test_get_block_extensions_5(self):
        code_ex = """
        public void methodEx(boolean a){
           RClass r = getR();
           if (a) {
               r.update();
           }
           System.out.println('Message');
           do1(r);
           do2(a);
           r = replaceR();
           do3(r);
        }"""
        manager = ProgramGraphsManager(code_ex, Lang.JAVA)
        block = manager.get_statements_in_range(Point(2, 0), Point(5, 10000))
        result_extension_ranges = []
        for ext in get_block_extensions(block, manager, code_ex.split("\n")):
            _range = [(r[0].line_number, r[1].line_number)
                      for r in ext.ranges]
            result_extension_ranges.append(_range)
        expected_extension_ranges = [[(2, 2), (3, 3), (4, 4), (5, 5)],
                                     [(2, 2), (3, 3), (4, 4), (5, 5), (7, 7), (9, 9), (10, 10)]]

        self.assertEqual(sorted(expected_extension_ranges),
                         sorted(result_extension_ranges))

    def test_get_block_extensions_6(self):
        code_ex = """
        public void methodEx(boolean a){
           RClass r = getR();
           if (a) {
               r.update();
           }
           System.out.println('Message');
           do1(r);
        }"""
        manager = ProgramGraphsManager(code_ex, Lang.JAVA)
        block = manager.get_statements_in_range(Point(2, 0), Point(2, 10000))
        result_extension_ranges = []
        for ext in get_block_extensions(block, manager, code_ex.split("\n")):
            _range = [(r[0].line_number, r[1].line_number)
                      for r in ext.ranges]
            result_extension_ranges.append(_range)
        expected_extension_ranges = [[(2, 2)]]

        self.assertEqual(sorted(expected_extension_ranges),
                         sorted(result_extension_ranges))

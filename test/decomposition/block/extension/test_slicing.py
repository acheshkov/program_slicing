__licence__ = 'MIT'
__author__ = 'KatGarmash'
__credits__ = ['KatGarmash']
__maintainer__ = 'KatGarmash'
__date__ = '2021/09/14'


import unittest

from program_slicing.decomposition.block.extension import slicing
from program_slicing.decomposition.block.extension.slicing import get_extended_block_slices_ordered, \
    get_extended_block_slices
from program_slicing.decomposition.program_slice import ProgramSlice
from program_slicing.graph.manager import ProgramGraphsManager
from program_slicing.graph.parse import Lang
from program_slicing.graph.point import Point

get_block_extensions = slicing.__get_block_extensions
get_incoming_variables = slicing.__get_incoming_variables
get_outgoing_variables = slicing.__get_outgoing_variables
extend_block_singleton = slicing.__extend_block_singleton
filter_anti_dependence = slicing.__filter_anti_dependence
filter_more_than_one_outgoing = slicing.__filter_more_than_one_outgoing
filter_control_dependence = slicing.__filter_control_dependence


class ExtendedBlockSlicingTestCase(unittest.TestCase):

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
        extension_generator = get_extended_block_slices_ordered(code_ex, slice_to_expand)
        found_extensions = {next(extension_generator) for _ in range(3)}
        self.assertEqual(expected_extensions, found_extensions)

    @unittest.skip("not implemented")
    def test_vars_before_2(self) -> None:
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
        extension_generator = get_extended_block_slices_ordered(code_ex, slice_to_expand)
        found_extension = next(extension_generator)
        self.assertEqual(expected_extension, found_extension)

    @unittest.skip("not implemented")
    def test_expand_invalid_slice_1(self) -> None:
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
        self.assertRaises(Exception, get_extended_block_slices_ordered(code_ex, slice_to_expand))

    @unittest.skip("not implemented")
    def test_expand_invalid_slice_2(self) -> None:
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
        extension_generator = get_extended_block_slices_ordered(code_ex, slice_to_expand)
        found_extensions = {next(extension_generator) for _ in range(3)}
        self.assertEqual(expected_extensions, found_extensions)

    @unittest.skip("not implemented")
    def test_vars_after(self) -> None:
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
        extension_generator = get_extended_block_slices_ordered(code_ex_after, slice_to_expand)
        found_extension = next(extension_generator)
        self.assertEqual(expected_extension, found_extension)

    @unittest.skip("not implemented")
    def test_multiple_vars(self) -> None:
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
        get_extended_block_slices_ordered(code_ex_multiple_vars, slice_to_expand)
        extension_generator = get_extended_block_slices_ordered(code_ex_multiple_vars, slice_to_expand)
        found_extensions = {next(extension_generator) for _ in range(3)}
        self.assertEqual(expected_extensions, found_extensions)

    def test_get_incoming_variables_1(self) -> None:
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

    def test_get_incoming_variables_2(self) -> None:
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

    def test_get_incoming_variables_3(self) -> None:
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

    def test_get_incoming_variables_4(self) -> None:
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
        block = manager.get_statements_in_range(Point(6, 0), Point(9, 10000))
        incoming_variables = get_incoming_variables(block, manager)
        self.assertEqual(set(incoming_variables.keys()), {'opt', 'a'})

    def test_outgoing_variables_1(self) -> None:
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

    def test_outgoing_variables_2(self) -> None:
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

    def test_extend_block_singleton_1(self) -> None:
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
            name_to_extension[ext[-1]] = ext[0]
        self.assertEqual({'a'}, set(name_to_extension.keys()))
        _range = [
            (r[0].line_number, r[1].line_number)
            for r in ProgramSlice(code.split("\n")).from_statements(name_to_extension['a']).ranges_compact
        ]
        self.assertEqual(sorted([(2, 2), (5, 5)]), _range)

    def test_extend_block_singleton_2(self) -> None:
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
            name_to_extension[ext[-1]] = ext[0]
        self.assertEqual({'opt', 'rest', 'i'}, set(name_to_extension.keys()))
        _range_opt = [
            (r[0].line_number, r[1].line_number)
            for r in ProgramSlice(code.split("\n")).from_statements(name_to_extension['opt']).ranges_compact
        ]
        self.assertEqual([(2, 2), (6, 8)], _range_opt)
        _range_rest = [
            (r[0].line_number, r[1].line_number)
            for r in ProgramSlice(code.split("\n")).from_statements(name_to_extension['rest']).ranges_compact
        ]
        self.assertEqual([(3, 3), (6, 8)], _range_rest)
        _range_i = [
            (r[0].line_number, r[1].line_number)
            for r in ProgramSlice(code.split("\n")).from_statements(name_to_extension['i']).ranges_compact
        ]
        self.assertEqual([(4, 4), (6, 8)], _range_i)

    def test_extend_block_singleton_3(self) -> None:
        code = """
        public void methodEx(ACl a){
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
            name_to_extension[ext[-1]] = ext[0]
        self.assertEqual({'r'}, set(name_to_extension.keys()))
        _range = [
            (r[0].line_number, r[1].line_number)
            for r in ProgramSlice(code.split("\n")).from_statements(name_to_extension['r']).ranges_compact
        ]
        self.assertEqual(sorted([(2, 5), (7, 7)]), sorted(_range))

    def test_extend_block_singleton_4(self) -> None:
        code = """
        public void methodEx(boolean a){
            System.out.println();
            if (cond(a)) {
                bla();
            }
        } """
        manager = ProgramGraphsManager(code, Lang.JAVA)
        block = manager.get_statements_in_range(Point(3, 0), Point(5, 10000))
        singleton_extensions = extend_block_singleton(block, manager)
        name_to_extension = {}
        for ext in singleton_extensions:
            name_to_extension[ext[-1]] = ext[0]
        self.assertEqual({'a'}, set(name_to_extension.keys()))
        _range = [
            (r[0].line_number, r[1].line_number)
            for r in ProgramSlice(code.split("\n")).from_statements(name_to_extension['a']).ranges_compact
        ]
        self.assertEqual(sorted([(3, 5)]), sorted(_range))

    def test_filter_anti_dependence_negative(self) -> None:
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

    def test_filter_anti_dependence_negative_2(self) -> None:
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

    @unittest.skip("Object DDG")
    def test_filter_anti_dependence_negative_3(self) -> None:
        """
        extended slice [(1, 1), (3,3)] -- we should filter such examples
        """
        code = """
           public void methodEx(SomeClass o) {
               int a = 1;
               o.change();
               do2(a, o);
           }"""
        manager = ProgramGraphsManager(code, Lang.JAVA)
        block = manager.get_statements_in_range(Point(4, 0), Point(4, 10000))
        extension = manager.get_statements_in_range(Point(2, 0), Point(2, 10000))
        self.assertFalse(filter_anti_dependence(extension.difference(block), block, manager))

    def test_filter_anti_dependence_positive(self) -> None:
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

    def test_filter_more_than_one_outgoing_negative_1(self) -> None:
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

    def test_filter_more_than_one_outgoing_negative_2(self) -> None:
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

    def test_filter_more_than_one_outgoing_negative_3(self) -> None:
        code = """
        public void methodEx() {
            SomeClass o = new SomeClass();
            int b = 2;
            int i = do2(o) + b;
        }"""
        manager = ProgramGraphsManager(code, Lang.JAVA)
        slice_candidate = manager.get_statements_in_range(Point(2, 0), Point(3, 10000))
        self.assertFalse(filter_more_than_one_outgoing(slice_candidate, manager))

    def test_filter_more_than_one_outgoing_positive_1(self) -> None:
        code = """
        public void methodEx() {
            int i = 1;
            int b = 2;
            i = b + 2;
        }"""
        manager = ProgramGraphsManager(code, Lang.JAVA)
        slice_candidate = manager.get_statements_in_range(Point(3, 0), Point(4, 10000))
        self.assertTrue(filter_more_than_one_outgoing(slice_candidate, manager))

    def test_filter_more_than_one_outgoing_positive_2(self) -> None:
        code = """
        public void methodEx() {
            SomeClass o = new SomeClass();
            int b = 2;
            o.changeSmth();
            int i = b + 1;
            int a = i + do2(o);
        }"""
        manager = ProgramGraphsManager(code, Lang.JAVA)
        slice_candidate = manager.get_statements_in_range(Point(3, 0), Point(5, 10000))
        self.assertTrue(filter_more_than_one_outgoing(slice_candidate, manager))

    def test_filter_control_dependence_negative_1(self) -> None:
        code = """
        public void methodEx() {
            int a = 1;
            for (int i=1; i < 10 ; i++) {
                System.out.println('Something');
                do1(a);
            }
        }"""
        manager = ProgramGraphsManager(code, Lang.JAVA)
        block = manager.get_statements_in_range(Point(5, 0), Point(5, 10000))
        extension_1 = manager.get_statements_in_range(Point(2, 0), Point(3, 10000))
        extension_2 = manager.get_statements_in_range(Point(6, 0), Point(6, 10000))
        self.assertFalse(filter_control_dependence(extension_1.union(extension_2), block, manager))

    def test_filter_control_dependence_negative_2(self) -> None:
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

    def test_get_block_extensions_1(self) -> None:
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
            _range = [(r[0].line_number, r[1].line_number) for r in ext.ranges_compact]
            result_extension_ranges.append(_range)
        expected_extension_ranges = [
            [(6, 8)],
            [(2, 2), (6, 8)],
            [(3, 3), (6, 8)],
            [(2, 3), (6, 8)]
        ]
        self.assertEqual(
            sorted(expected_extension_ranges),
            sorted(result_extension_ranges))

    def test_get_block_extensions_2(self) -> None:
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
            _range = [(r[0].line_number, r[1].line_number) for r in ext.ranges_compact]
            result_extension_ranges.append(_range)
        expected_extension_ranges = [
            [(6, 8)],
            [(2, 2), (5, 9)]
        ]
        self.assertEqual(sorted(expected_extension_ranges), sorted(result_extension_ranges))

    def test_get_block_extensions_3(self) -> None:
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
            _range = [(r[0].line_number, r[1].line_number) for r in ext.ranges_compact]
            result_extension_ranges.append(_range)
        expected_extension_ranges = [
            [(6, 6)],
            [(4, 7)]
        ]
        self.assertEqual(
            sorted(expected_extension_ranges),
            sorted(result_extension_ranges))

    def test_get_block_extensions_4(self) -> None:
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
            _range = [(r[0].line_number, r[1].line_number) for r in ext.ranges_compact]
            result_extension_ranges.append(_range)
        expected_extension_ranges = [
            [(2, 2), (5, 10)],
            [(7, 9)]
        ]
        self.assertEqual(
            sorted(expected_extension_ranges),
            sorted(result_extension_ranges))

    def test_get_block_extensions_5(self) -> None:
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
            _range = [(r[0].line_number, r[1].line_number) for r in ext.ranges_compact]
            result_extension_ranges.append(_range)
        expected_extension_ranges = [
            [(2, 5)],
            [(2, 5), (7, 7), (9, 10)]]
        self.assertEqual(
            sorted(expected_extension_ranges),
            sorted(result_extension_ranges))

    def test_get_block_extensions_6(self) -> None:
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
            _range = [(r[0].line_number, r[1].line_number) for r in ext.ranges_compact]
            result_extension_ranges.append(_range)
        expected_extension_ranges = [[(2, 2)]]
        self.assertEqual(
            sorted(expected_extension_ranges),
            sorted(result_extension_ranges))

    def test_get_block_extensions_7(self) -> None:
        code_ex = """
           public void methodEx(boolean a){
              int c = 1;
              a = false;
              if (a) {
                  c ++;
              }
           }"""
        manager = ProgramGraphsManager(code_ex, Lang.JAVA)
        block = manager.get_statements_in_range(Point(4, 0), Point(6, 10000))
        result_extension_ranges = []
        for ext in get_block_extensions(block, manager, code_ex.split("\n")):
            _range = [(r[0].line_number, r[1].line_number) for r in ext.ranges_compact]
            result_extension_ranges.append(_range)
        expected_extension_ranges = [
            [(2, 6)],
            [(4, 6)],
            [(3, 6)],
            [(2, 2), (4, 6)]]
        self.assertEqual(
            sorted(expected_extension_ranges),
            sorted(result_extension_ranges))

    def test_get_block_extensions_8(self) -> None:
        code_ex = """
           public void methodEx(boolean a){
              int c = 1;
              a = false;
              c += 1;
              if (a) {
                  do2(c);
              }
           }"""
        manager = ProgramGraphsManager(code_ex, Lang.JAVA)
        block = manager.get_statements_in_range(Point(5, 0), Point(7, 10000))
        result_extension_ranges = []
        for ext in get_block_extensions(block, manager, code_ex.split("\n")):
            _range = [(r[0].line_number, r[1].line_number) for r in ext.ranges_compact]
            result_extension_ranges.append(_range)
        expected_extension_ranges = [
            [(2, 7)],
            [(2, 2), (4, 7)],
            [(3, 3), (5, 7)],
            [(5, 7)]]
        self.assertEqual(
            sorted(expected_extension_ranges),
            sorted(result_extension_ranges))

    def test_get_block_extensions_9(self) -> None:
        code_ex = """
        public void methodEx(final AClass a) {
            final int opt = a.getOpt();
            int i = 1;
            if (opt > 0) {
                if (i > 1) {
                    for (int j = 0; j < opt; j++, i++) {
                        System.out.println(opt);
                    }
                }
            }
        }"""
        manager = ProgramGraphsManager(code_ex, Lang.JAVA)
        block = manager.get_statements_in_range(Point(6, 0), Point(8, 10000))
        result_extension_ranges = []
        for ext in get_block_extensions(block, manager, code_ex.split("\n")):
            _range = [(r[0].line_number, r[1].line_number) for r in ext.ranges_compact]
            result_extension_ranges.append(_range)
        expected_extension_ranges = [
            [(6, 8)],
            [(2, 10)]
        ]
        self.assertEqual(sorted(expected_extension_ranges), sorted(result_extension_ranges))

    @unittest.skip("Object DDG")
    def test_get_block_extensions_10(self) -> None:
        code_ex = """
        public void methodEx(boolean a){
           RClass r = getR();
           boolean b = false;
           int c = 1;
           if (a) {
               c ++;
           }
           r.update1(b);
           r.update2(c);
        }"""
        manager = ProgramGraphsManager(code_ex, Lang.JAVA)
        block = manager.get_statements_in_range(Point(5, 0), Point(7, 10000))
        result_extension_ranges = []
        for ext in get_block_extensions(block, manager, code_ex.split("\n")):
            _range = [(r[0].line_number, r[1].line_number) for r in ext.ranges_compact]
            result_extension_ranges.append(_range)
        expected_extension_ranges = [
            [(5, 7)]]
        self.assertEqual(
            sorted(expected_extension_ranges),
            sorted(result_extension_ranges))

    @unittest.skip("Object DDG")
    def test_get_block_extensions_11(self) -> None:
        code_ex = """
            public void methodEx(LClass l){
               boolean a = l.getR();
               l.change();
               int c = 1;
               if (a) {
                   c++;
               }
            }"""
        manager = ProgramGraphsManager(code_ex, Lang.JAVA)
        block = manager.get_statements_in_range(Point(5, 0), Point(7, 10000))
        result_extension_ranges = []
        for ext in get_block_extensions(block, manager, code_ex.split("\n")):
            _range = [(r[0].line_number, r[1].line_number) for r in ext.ranges_compact]
            result_extension_ranges.append(_range)
        expected_extension_ranges = [
            [(5, 7)],
            [(4, 7)]]
        self.assertEqual(
            sorted(expected_extension_ranges),
            sorted(result_extension_ranges))

    def test_cyclic_dependencies_forward(self):
        """
        Makes sure doesn't go into infinite recursion due to cycle.
        """
        code = """
        public void methodEx() {
            int i = 1;
            while (condition()) {
                i++;
            }
        }
        """
        manager = ProgramGraphsManager(code, Lang.JAVA)
        block = manager.get_statements_in_range(Point(2, 0), Point(2, 10000))
        result_extension_ranges = []
        for ext in get_block_extensions(block, manager, code.split("\n")):
            _range = [(r[0].line_number, r[1].line_number) for r in ext.ranges_compact]
            result_extension_ranges.append(_range)
        expected_extension_ranges = [[(2, 2)]]
        self.assertEqual(
            sorted(expected_extension_ranges),
            sorted(result_extension_ranges))

    def test_cycle_ddg_cfg(self):
        code = """
        public void methodEx() {
            int i = 0;
            int b = 0;
            while (cond(i)) {
                do1(b, ++i);
            }
        }
        """
        manager = ProgramGraphsManager(code, Lang.JAVA)
        block = manager.get_statements_in_range(Point(5, 0), Point(5, 10000))
        result_extension_ranges = []
        for ext in get_block_extensions(block, manager, code.split("\n")):
            _range = [(r[0].line_number, r[1].line_number) for r in ext.ranges_compact]
            result_extension_ranges.append(_range)
        expected_extension_ranges = [
            [(5, 5)],
            [(2, 2), (4, 6)],
            [(2, 6)]]
        self.assertEqual(
            sorted(expected_extension_ranges),
            sorted(result_extension_ranges))

    def test_anon_class_function(self):
        """
        make sure we avoid methods defined in anon class
        """
        code = """
        public void methodEx() {
            int a = 0;
            doSomething(a);
            SomeClass o = new SomeClass() {
                public int greet() {
                    int b = 0;
                    return 1;
                }
            };
            doSomething(o);
        }
        """
        manager = ProgramGraphsManager(code, Lang.JAVA)
        block = manager.get_statements_in_range(Point(3, 0), Point(9, 10000))
        result_extension_ranges = []
        for ext in get_block_extensions(block, manager, code.split("\n")):
            _range = [(r[0].line_number, r[1].line_number) for r in ext.ranges_compact]
            result_extension_ranges.append(_range)
        expected_extension_ranges = [
            [(3, 9)],
            [(2, 9)],
            [(3, 10)],
            [(2, 10)]]
        self.assertEqual(
            sorted(expected_extension_ranges),
            sorted(result_extension_ranges))

    def test_noneffective(self):
        code = """
        public void methodEx() {
            int a = 1;

            // some comment
            do(a);
        }
        """
        manager = ProgramGraphsManager(code, Lang.JAVA)
        block = manager.get_statements_in_range(Point(5, 0), Point(5, 10000))
        result_extension_ranges = []
        for ext in get_block_extensions(block, manager, code.split("\n")):
            _range = [(r[0].line_number, r[1].line_number) for r in ext.ranges_compact]
            result_extension_ranges.append(_range)
        expected_extension_ranges = [[(2, 5)], [(5, 5)]]
        self.assertEqual(
            sorted(expected_extension_ranges),
            sorted(result_extension_ranges))

    def test_return_statement(self):
        code = """
        public int methodEx() {
            int a = 0;
            return a + 1;
        }
        """
        manager = ProgramGraphsManager(code, Lang.JAVA)
        block = manager.get_statements_in_range(Point(3, 0), Point(3, 10000))
        result_extension_ranges = []
        for ext in get_block_extensions(block, manager, code.split("\n")):
            _range = [(r[0].line_number, r[1].line_number) for r in ext.ranges_compact]
            result_extension_ranges.append(_range)
        expected_extension_ranges = [[(2, 3)], [(3, 3)]]
        self.assertEqual(
            sorted(expected_extension_ranges),
            sorted(result_extension_ranges))

    def test_for_scope(self):
        code = """
        public void methodEx() {
            for (int i = 0; i < 10; i++) {
                do1(i);
            }
        }
        """
        ext_blocks = get_extended_block_slices(code, Lang.JAVA)
        result_ranges = []
        for ext in ext_blocks:
            _range = [(r[0].line_number, r[1].line_number) for r in ext.ranges_compact]
            result_ranges.append(_range)
        expected_extension_ranges = [[(2, 4)], [(3, 3)]]
        self.assertEqual(
            sorted(expected_extension_ranges),
            sorted(result_ranges))

    def test_while_scope(self):
        code = """
        public void methodEx() {
            int i = 1;
            while (i < 10) {
                do1(i);
                i++;
            }
        }
        """
        ext_blocks = get_extended_block_slices(code, Lang.JAVA)
        result_ranges = []
        for ext in ext_blocks:
            _range = [(r[0].line_number, r[1].line_number) for r in ext.ranges_compact]
            result_ranges.append(_range)
        expected_extension_ranges = [[(2, 2)], [(4, 4)], [(5, 5)], [(4, 5)], [(3, 6)], [(2, 6)]]
        self.assertEqual(
            sorted(expected_extension_ranges),
            sorted(result_ranges))

    def test_if_scope(self):
        code = """
        public void methodEx() {
            int i = 1;
            if (cond2(i)) {
                do1(i);
            }
        }
        """
        ext_blocks = get_extended_block_slices(code, Lang.JAVA)
        result_ranges = []
        for ext in ext_blocks:
            _range = [(r[0].line_number, r[1].line_number) for r in ext.ranges_compact]
            result_ranges.append(_range)
        expected_extension_ranges = [[(2, 2)], [(4, 4)], [(3, 5)], [(2, 5)]]
        self.assertEqual(
            sorted(expected_extension_ranges),
            sorted(result_ranges))

    def test_return(self):
        code = """
        public int methodEx() {
            int i = 1;
            while (i < 10) {
                do1(i);
                i++;
            }
            return i;
        }
        """
        ext_blocks = get_extended_block_slices(code, Lang.JAVA)
        result_ranges = []
        for ext in ext_blocks:
            _range = [(r[0].line_number, r[1].line_number) for r in ext.ranges_compact]
            result_ranges.append(_range)
        expected_extension_ranges = [
            [(2, 2)],
            [(4, 4)],
            [(5, 5)],
            [(4, 5)],
            [(3, 6)],
            [(2, 6)],
            [(3, 7)],
            [(2, 7)],
            [(7, 7)]]
        self.assertEqual(
            sorted(expected_extension_ranges),
            sorted(result_ranges))

    def test_included_scope(self):
        code = """
        public void methodEx() {
            if (cond()) {
                int i = 1;
                if (cond2(i)) {
                    do1(i);
                }
            }
        }
        """
        ext_blocks = get_extended_block_slices(code, Lang.JAVA)
        result_ranges = []
        for ext in ext_blocks:
            _range = [(r[0].line_number, r[1].line_number) for r in ext.ranges_compact]
            result_ranges.append(_range)
        expected_extension_ranges = [
            [(3, 3)],
            [(5, 5)],
            [(4, 6)],
            [(3, 6)],
            [(2, 7)]]
        self.assertEqual(
            sorted(expected_extension_ranges),
            sorted(result_ranges))

    @unittest.skip("BUG: if without curly braces doesnt have SCOPE, hence not handled correctly")
    def test_if_else_scope(self):
        code = """
        public void methodEx() {
            if (cond())
                do1();
            else
                do2();
        }
        """
        ext_blocks = get_extended_block_slices(code, Lang.JAVA)
        result_ranges = []
        for ext in ext_blocks:
            _range = [(r[0].line_number, r[1].line_number) for r in ext.ranges_compact]
            result_ranges.append(_range)
        expected_extension_ranges = [[(3, 3)], [(5, 5)], [(2, 5)]]
        self.assertEqual(
            sorted(expected_extension_ranges),
            sorted(result_ranges))

    def __compare_extended_slices(self, **kwargs) -> None:
        result_extension = kwargs["extension"]
        expected_range = kwargs["expected_range"]
        expected_in = kwargs["expected_in"]
        expected_out = kwargs["expected_out"]
        source_lines = kwargs['source_code'].split("\n")
        _range = [
            (r[0].line_number, r[1].line_number)
            for r in ProgramSlice(source_lines).from_statements(result_extension[0]).ranges_compact
        ]
        in_vars = set(result_extension[1].keys())
        out_vars = set(result_extension[2].keys())
        self.assertEqual(expected_range, _range)
        self.assertEqual(expected_in, in_vars)
        self.assertEqual(expected_out, out_vars)

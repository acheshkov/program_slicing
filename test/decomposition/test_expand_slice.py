from unittest import TestCase

from program_slicing.decomposition.expand_slice import expand_slices_ordered

class ExpandSliceTestCase(TestCase):

        code_ex_before = '''public Operand receiveArgs(final ArgsNode argsNode, IR_Scope s) {
                            final int required = argsNode.getRequiredArgsCount();
                            final int opt = argsNode.getOptionalArgsCount();
                            final int rest = argsNode.getRestArg();
                            
                            int argIndex = 1;
                    
                            ListNode preArgs  = argsNode.getPre();
                            for (int i = 0; i < required; i++, argIndex++) {
                                ArgumentNode a = (ArgumentNode)preArgs.get(i);
                                if (a instanceof TypedArgumentNode) {
                                    TypedArgumentNode t = (TypedArgumentNode)a;
                                    s.addInstr(new DECLARE_LOCAL_TYPE_Instr(argIndex, buildType(t.getTypeNode())));
                                }
                            }
                    
                            if (opt > 0 || rest > -1) {
                                ListNode optArgs = argsNode.getOptArgs();
                                for (int j = 0; j < opt; j++, argIndex++) {
                                    Label l = s.getNewLabel();
                                    LocalAsgnNode n = (LocalAsgnNode)optArgs.get(j);
                                    s.addInstr(new RECV_OPT_ARG_Instr(new LocalVariable(n.getName()), argIndex, l));
                                }
                    
                                if (rest > -1) {
                                    s.addInstr(new ReceiveArgumentInstruction(new LocalVariable(argsNode.getRestArgNode().getName()), argIndex, true));
                                    argIndex++;
                                }
                            }
                        }'''

        code_ex_after = '''public void freeEntry(BasicPoolEntry entry, boolean reusable, long validDuration, TimeUnit timeUnit) {        
                        RouteSpecificPool rospl = getRoutePool(route, true);
                        if (reusable) {
                            if (log.isDebugEnabled()) {
                                String s;
                                if (validDuration > 0) {
                                    s = "for " + validDuration + " " + timeUnit;
                                } else {
                                    s = "indefinitely";
                                }
                                log.debug("Pooling connection" +
                                        " [" + route + "][" + entry.getState() + "]; keep alive " + s);
                            }
                            rospl.freeEntry(entry);
                            entry.updateExpiry(validDuration, timeUnit);
                            freeConnections.add(entry);
                        } else {
                            rospl.dropEntry();
                            numConnections--;
                        }
                        System.out.println('Something');
                        notifyWaitingThread(rospl);
                        someCommand(reusable);
                    }'''

        code_ex_simple = '''public void simpleMethod() {
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

    def test_vars_before_1(self):
        """
        output the first 3 minimal expansions from the priority queue
        """
        slice_to_expand = (18, 30)
        expected_extensions = {[3], [4], [3, 4]}
        extension_generator = expand_slices_ordered(self.code_ex_before, slice_to_expand)
        found_extensions = {next(extension_generator) for _ in range(3)}
        self.assertSetEqual(expected_extensions, found_extensions)

    def test_vars_before_2(self):
        """
        output the minimal expansion
        """
        slice_to_expand = (19, 23)
        expected_extension = [18]
        extension_generator = expand_slices_ordered(self.code_ex_before, slice_to_expand)
        found_extension = next(extension_generator)
        self.assertListEqual(expected_extension, found_extension)

    def test_expand_invalid_slice_1(self):
        """
        slice not finished in the end
        """
        slice_to_expand = (17, 21)
        expected_extensions = {[18], [22], [18, 22]}
        extension_generator = expand_slices_ordered(self.code_ex_before, slice_to_expand)
        found_extensions = {next(extension_generator) for _ in range(3)}
        self.assertSetEqual(expected_extensions, found_extensions)

    def test_expand_invalid_slice_2(self):
        """
        needs expanding from beginning: 3 expansions of equal cost
        """
        slice_to_expand = (7, 9)
        expected_extensions = {[4, 5, 6], [3, 4, 5, 6], [2, 3, 4, 5, 6]}
        extension_generator = expand_slices_ordered(self.code_ex_before, slice_to_expand)
        found_extensions = {next(extension_generator) for _ in range(3)}
        self.assertSetEqual(expected_extensions, found_extensions)

    def test_vars_after(self):
        """
        output first 3 minimal expansions from the priority queue
        (they reduce the number of IN)
        """
        slice_to_expand = (2, 20)
        expected_extensions = {[22], [23], [22, 23]}
        extension_generator = expand_slices_ordered(self.code_ex_after, slice_to_expand)
        found_extensions = {next(extension_generator) for _ in range(3)}
        self.assertSetEqual(expected_extensions, found_extensions)

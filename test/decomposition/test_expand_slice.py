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

    def test_vars_before(self):
        """
        output first 3 minimal expansions from the priority queue
        (they reduce the number of IN)
        """
        slice_to_expand = (18, 30)
        expected_extensions = {[3], [4], [3, 4]}
        extension_generator = expand_slices_ordered(self.code_ex_before, slice_to_expand)
        found_extensions = {next(extension_generator) for _ in range(3)}
        self.assertSetEqual(expected_extensions, found_extensions)



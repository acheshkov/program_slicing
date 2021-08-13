    public Operand receiveArgs(final ArgsNode argsNode, IR_Scope s) {
        final int required = argsNode.getRequiredArgsCount();
        final int opt = argsNode.getOptionalArgsCount();
        final int rest = argsNode.getRestArg();

        s.addInstr(new ReceiveArgumentInstruction(s.getSelf(), 0));

        // Other args begin at index 1
        int argIndex = 1;

        // Both for fixed arity and variable arity methods
        ListNode preArgs  = argsNode.getPre();
        for (int i = 0; i < required; i++, argIndex++) {
            ArgumentNode a = (ArgumentNode)preArgs.get(i);
            if (a instanceof TypedArgumentNode) {
                TypedArgumentNode t = (TypedArgumentNode)a;
                s.addInstr(new DECLARE_LOCAL_TYPE_Instr(argIndex, buildType(t.getTypeNode())));
            }
            s.addInstr(new ReceiveArgumentInstruction(new LocalVariable(a.getName()), argIndex));
        }

        if (argsNode.getBlock() != null)
            s.addInstr(new RECV_CLOSURE_Instr(new LocalVariable(argsNode.getBlock().getName())));

        // Now for the rest
        if (opt > 0 || rest > -1) {
            ListNode optArgs = argsNode.getOptArgs();
            for (int j = 0; j < opt; j++, argIndex++) {
                    // Jump to 'l' if this arg is not null.  If null, fall through and build the default value!
                Label l = s.getNewLabel();
                LocalAsgnNode n = (LocalAsgnNode)optArgs.get(j);
                s.addInstr(new RECV_OPT_ARG_Instr(new LocalVariable(n.getName()), argIndex, l));
                build(n, s);
                s.addInstr(new LABEL_Instr(l));
            }

            if (rest > -1) {
                s.addInstr(new ReceiveArgumentInstruction(new LocalVariable(argsNode.getRestArgNode().getName()), argIndex, true));
                argIndex++;
            }
        }

        return null;
    }
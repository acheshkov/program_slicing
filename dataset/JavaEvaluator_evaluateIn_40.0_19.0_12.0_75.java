private Value evaluateIn (org.netbeans.modules.debugger.jpda.expr.JavaExpression expression,
                              CallStackFrame csf,
                              final StackFrame frame, int frameDepth,
                              ObjectReference var, CompilationInfoHolder ciHolder,
                              boolean canInvokeMethods,
                              Runnable methodInvokePreprocessor) throws InvalidExpressionException {
        // should be already synchronized on the frame's thread
        if (csf == null)
            throw new InvalidExpressionException
                    (NbBundle.getMessage(JPDADebuggerImpl.class, "MSG_NoCurrentContext"));

        // TODO: get imports from the source file
        CallStackFrameImpl csfi = (CallStackFrameImpl) csf;
        List<String> imports = new ImportsLazyList(csfi);
        List<String> staticImports = new ArrayList<String>();
        try {
            JPDAThreadImpl trImpl = (JPDAThreadImpl) csf.getThread();
            EvaluationContext context;
            TreeEvaluator evaluator =
                expression.evaluator(
                    context = new EvaluationContext(
                        trImpl,
                        frame,
                        frameDepth,
                        var,
                        imports,
                        staticImports,
                        canInvokeMethods,
                        methodInvokePreprocessor,
                        debugger,
                        vmCache
                    ),
                    ciHolder
                );
            try {
                Value v = evaluator.evaluate ();
                TreePath treePath = context.getTreePath();
                if (treePath != null) {
                    Tree tree = treePath.getLeaf();
                    EvaluationContext.VariableInfo vi = context.getVariableInfo(tree);
                    if (vi != null) {
                        valueContainers.put(v, vi);
                    }
                }
                return v;
            } finally {
                if (debugger.methodCallsUnsupportedExc == null && !context.canInvokeMethods()) {
                    debugger.methodCallsUnsupportedExc =
                            new InvalidExpressionException(new UnsupportedOperationException());
                }
                context.destroy();
            }
        } catch (InternalExceptionWrapper e) {
            throw new InvalidExpressionException(e.getLocalizedMessage());
        } catch (ObjectCollectedExceptionWrapper e) {
            throw new InvalidExpressionException(NbBundle.getMessage(
                TreeEvaluator.class, "CTL_EvalError_collected"));
        } catch (VMDisconnectedExceptionWrapper e) {
            throw new InvalidExpressionException(NbBundle.getMessage(
                TreeEvaluator.class, "CTL_EvalError_disconnected"));
        } catch (InvalidStackFrameExceptionWrapper e) {
            JPDAThreadImpl t = (JPDAThreadImpl) csf.getThread();
            e = Exceptions.attachMessage(e, t.getThreadStateLog());
            Exceptions.printStackTrace(Exceptions.attachMessage(e, "During evaluation of '"+expression.getExpression()+"'")); // Should not occur
            throw new InvalidExpressionException (NbBundle.getMessage(
                    JPDAThreadImpl.class, "MSG_NoCurrentContext"));
        } catch (EvaluationException e) {
            InvalidExpressionException iee = new InvalidExpressionException (e);
            Exceptions.attachMessage(iee, "Expression = '"+expression.getExpression()+"'");
            throw iee;
        } catch (IncompatibleThreadStateException itsex) {
            InvalidExpressionException isex = new InvalidExpressionException(itsex.getLocalizedMessage());
            isex.initCause(itsex);
            throw isex;
        }
    }
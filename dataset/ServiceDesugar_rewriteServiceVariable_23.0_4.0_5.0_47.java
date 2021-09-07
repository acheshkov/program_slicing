void rewriteServiceVariable(BLangService service, SymbolEnv env, BLangBlockStmt attachments) {
        // service x on y { ... }
        //
        // after desugar :
        //      if y is anonymous (globalVar)   ->      y = y(expr)
        //      (init)                          ->      y.__attach(x, {});

        if (service.isAnonymousService()) {
            return;
        }
        final DiagnosticPos pos = service.pos;

        int count = 0;
        for (BLangExpression attachExpr : service.attachedExprs) {
            //      if y is anonymous   ->      y = y(expr)
            BLangSimpleVarRef listenerVarRef;
            if (attachExpr.getKind() == NodeKind.SIMPLE_VARIABLE_REF) {
                listenerVarRef = (BLangSimpleVarRef) attachExpr;
            } else {
                // Define anonymous listener variable.
                BLangSimpleVariable listenerVar = ASTBuilderUtil
                        .createVariable(pos, LISTENER + service.name.value + count++, attachExpr.type, attachExpr,
                                null);
                ASTBuilderUtil.defineVariable(listenerVar, env.enclPkg.symbol, names);
                listenerVar.symbol.flags |= Flags.LISTENER;
                env.enclPkg.globalVars.add(listenerVar);
                listenerVarRef = ASTBuilderUtil.createVariableRef(pos, listenerVar.symbol);
            }

            //      (.<init>)              ->      y.__attach(x, {});
            // Find correct symbol.
            final Name functionName = names
                    .fromString(Symbols.getAttachedFuncSymbolName(attachExpr.type.tsymbol.name.value, ATTACH_METHOD));
            BInvokableSymbol methodRef = (BInvokableSymbol) symResolver
                    .lookupMemberSymbol(pos, ((BObjectTypeSymbol) listenerVarRef.type.tsymbol).methodScope, env,
                            functionName, SymTag.INVOKABLE);

            // Create method invocation
            List<BLangExpression> args = new ArrayList<>();
            args.add(ASTBuilderUtil.createVariableRef(pos, service.variableNode.symbol));

            BLangLiteral serviceName = ASTBuilderUtil.createLiteral(pos, symTable.stringType, service.name.value);
            List<BLangNamedArgsExpression> namedArgs = Collections.singletonList(
                    ASTBuilderUtil.createNamedArg("name", serviceName));

            addMethodInvocation(pos, listenerVarRef, methodRef, args, namedArgs, attachments);
        }
    }
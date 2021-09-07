@Override
    public void visit(PHPDocMethodTag node) {
        AnnotationParsedLine kind = node.getKind();
        Scope currentScope = modelBuilder.getCurrentScope();
        boolean scopeHasBeenModified = false;
        // Someone uses @method tag in method scope :/ So we have to simulate that it's defined in class scope...
        if (currentScope instanceof MethodScope) {
            MethodScope methodScope = (MethodScope) currentScope;
            currentScope = methodScope.getInScope();
            modelBuilder.setCurrentScope((ScopeImpl) currentScope);
            scopeHasBeenModified = true;
        }
        if (currentScope instanceof TypeScope && kind.equals(PHPDocTag.Type.METHOD)) {
            modelBuilder.buildMagicMethod(node, occurencesBuilder);
            occurencesBuilder.prepare(node, currentScope);
        }
        // ...and then reset it to avoid possible problems.
        if (scopeHasBeenModified) {
            modelBuilder.reset();
        }
        if (currentScope instanceof TypeScope) {
            MethodScopeImpl methodScope = MethodScopeImpl.createElement(currentScope, node);
            modelBuilder.setCurrentScope(methodScope);
        } else {
            modelBuilder.setCurrentScope((ScopeImpl) currentScope);
        }
        super.visit(node);
        modelBuilder.reset();
    }
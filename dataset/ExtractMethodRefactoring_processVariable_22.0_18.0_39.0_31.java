private void processVariable(List<ITypeBinding> result, IVariableBinding variable, int modifier) {
		if (variable == null) {
			return;
		}
		ITypeBinding binding = variable.getType();
		if (binding != null && binding.isParameterizedType()) {
			ITypeBinding[] typeArgs = binding.getTypeArguments();
			for (int args = 0; args < typeArgs.length; args++) {
				ITypeBinding arg = typeArgs[args];
				if (arg.isTypeVariable() && !result.contains(arg)) {
					ASTNode decl = fRoot.findDeclaringNode(arg);
					if (decl != null) {
						ASTNode parent = decl.getParent();
						if (parent instanceof MethodDeclaration || (parent instanceof TypeDeclaration && Modifier.isStatic(modifier))) {
							result.add(arg);
						}
					}
				} else {
					ITypeBinding bound = arg.getBound();
					if (arg.isWildcardType() && bound != null && !result.contains(bound)) {
						ASTNode decl = fRoot.findDeclaringNode(bound);
						if (decl != null) {
							ASTNode parent = decl.getParent();
							if (parent instanceof MethodDeclaration || (parent instanceof TypeDeclaration && Modifier.isStatic(modifier))) {
								result.add(bound);
							}
						}
					}
				}
			}
		}
	}
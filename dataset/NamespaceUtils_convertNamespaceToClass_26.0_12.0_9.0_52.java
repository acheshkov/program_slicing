public static GhidraClass convertNamespaceToClass(Namespace namespace)
			throws InvalidInputException {

		Symbol namespaceSymbol = namespace.getSymbol();
		String name = namespaceSymbol.getName();
		SourceType originalSource = namespaceSymbol.getSource();

		SymbolTable symbolTable = namespaceSymbol.getProgram().getSymbolTable();

		// Temporarily rename old namespace (it will be removed at the end)
		int count = 1;
		while (true) {
			String n = name + "_" + count++;
			try {
				namespaceSymbol.setName(n, SourceType.ANALYSIS);
				break;
			}
			catch (DuplicateNameException e) {
				// continue
			}
			catch (InvalidInputException e) {
				throw new AssertException(e);
			}
		}

		// create new class namespace
		GhidraClass classNamespace = null;
		try {
			classNamespace =
				symbolTable.createClass(namespace.getParentNamespace(), name, originalSource);
		}
		catch (DuplicateNameException e) {
			throw new AssertException(e);
		}
		catch (InvalidInputException e) {
			// The only cause of this exception can be assumed but we need to
			// avoid showing the user a temporary name
			throw new InvalidInputException(
				"Namespace contained within Function may not be converted to a class: " + name);
		}

		// move everything from old namespace into new class namespace
		try {
			for (Symbol s : symbolTable.getSymbols(namespace)) {
				s.setNamespace(classNamespace);
			}
			namespaceSymbol.delete();
		}
		catch (DuplicateNameException | InvalidInputException | CircularDependencyException e) {
			throw new AssertException(e);
		}
		return classNamespace;
	}
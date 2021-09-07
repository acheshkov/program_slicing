public static Symbol createPreferredLabelOrFunctionSymbol(Program program, Address address,
			Namespace namespace, String name, SourceType source) throws InvalidInputException {

		try {
			if (!address.isMemoryAddress()) {
				throw new IllegalArgumentException("expected memory address");
			}
			if (namespace == null) {
				namespace = program.getGlobalNamespace();
			}

			SymbolTable symbolTable = program.getSymbolTable();

			// check for symbol already existing at address
			Symbol symbol = symbolTable.getSymbol(name, address, namespace);
			if (symbol != null) {
				return symbol;
			}

			if (namespace.isGlobal()) {
				// do not add global symbol if same name already exists at address
				for (Symbol s : program.getSymbolTable().getSymbols(address)) {
					if (name.equals(s.getName())) {
						return null;
					}
				}
			}
			else {
				// change namespace on global symbol with same name
				symbol = symbolTable.getGlobalSymbol(name, address);
				if (symbol != null) {
					symbol.setNamespace(namespace);
					return symbol;
				}
			}

			// create new symbol if needed
			return symbolTable.createLabel(address, name, namespace, source);
		}
		catch (DuplicateNameException | CircularDependencyException e) {
			throw new AssertException(e);
		}
	}
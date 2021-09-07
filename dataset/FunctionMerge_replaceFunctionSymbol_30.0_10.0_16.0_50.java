Symbol replaceFunctionSymbol(Address originEntryPoint, LongLongHashtable conflictSymbolIDMap,
			TaskMonitor monitor)
			throws DuplicateNameException, InvalidInputException, CircularDependencyException {

		// Assumes: The function in the destination program should already be replaced at this point.
		Address resultEntryPoint = originToResultTranslator.getAddress(originEntryPoint);
		Function fromFunction = fromFunctionManager.getFunctionAt(originEntryPoint);
		Function toFunction = toFunctionManager.getFunctionAt(resultEntryPoint);
		if ((fromFunction != null) && (toFunction != null)) {
			String fromName = fromFunction.getName();
			Symbol fromSymbol = fromFunction.getSymbol();
			SourceType fromSource = fromSymbol.getSource();
			Namespace fromNamespace = fromSymbol.getParentNamespace();
			Namespace expectedToNamespace = DiffUtility.getNamespace(fromNamespace, toProgram);
			if (expectedToNamespace != null) {
				Symbol existingSymbol = toProgram.getSymbolTable().getSymbol(fromName,
					originEntryPoint, expectedToNamespace);
				if (existingSymbol != null) {
					// TODO Change the function symbol to this one. // FIXME
				}
			}
			String toName = toFunction.getName();
			Symbol toSymbol = toFunction.getSymbol();
			Namespace currentToNamespace = toSymbol.getParentNamespace();
			Symbol expectedNamespaceSymbol =
				SimpleDiffUtility.getSymbol(fromNamespace.getSymbol(), toProgram);
			boolean sameNamespace = currentToNamespace.getSymbol() == expectedNamespaceSymbol;
			if (fromName.equals(toName) && sameNamespace) {
				return toSymbol; // function symbol name and namespace match.
			}
			Namespace desiredToNamespace = currentToNamespace;
			if (!sameNamespace) {
				desiredToNamespace = new SymbolMerge(fromProgram, toProgram).resolveNamespace(
					fromNamespace, conflictSymbolIDMap);
			}
			// Rename the function so that we will be able to move it.
			boolean hasDifferentName = !fromName.equals(toName);
			if (hasDifferentName) {
				toFunction.setName(fromName, fromSource);
			}
			// Move it to the new namespace.
			if (currentToNamespace != desiredToNamespace) {
				toFunction.setParentNamespace(desiredToNamespace);
			}

			// TODO May want to save the symbol info if the function didn't get desired pathname. // FIXME

			return toFunction.getSymbol();
		}
		return null;
	}
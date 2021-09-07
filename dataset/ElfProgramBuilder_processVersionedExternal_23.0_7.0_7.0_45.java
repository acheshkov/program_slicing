private boolean processVersionedExternal(ElfSymbol elfSymbol) {

		String symName = elfSymbol.getNameAsString();
		int index = symName.indexOf("@");
		if (index < 0) {
			return false;
		}

		// TODO: Versioned symbols may also exist on real addresses
		// corresponding to external linkages in the .got, .plt and 
		// other memory locations which may relate to external functions.
		// Unsure if this approach is appropriate since we are not 
		// handling these versioned symbols in a consistent fashion,
		// however their existence can interfere with demangling for
		// externals and related thunks.

		if (lastExternalBlockEntryAddress == null) {
			return false;
		}

		int altIndex = symName.indexOf("@@");
		if (altIndex > 0) {
			index = altIndex;
		}
		String realName = symName.substring(0, index);

		// Find real symbol (assumes real symbol is always processed first)
		Symbol s = findExternalBlockSymbol(realName, externalBlockLimits.getMinAddress(),
			lastExternalBlockEntryAddress);
		if (s == null) {
			return false;
		}

		// Add versioned symbol as comment only
		Address address = s.getAddress();
		String comment = listing.getComment(CodeUnit.PRE_COMMENT, address);
		if (comment == null || comment.length() == 0) {
			comment = symName;
		}
		else {
			comment += "\n" + symName;
		}
		listing.setComment(address, CodeUnit.PRE_COMMENT, comment);
		setElfSymbolAddress(elfSymbol, address);
		return true;
	}
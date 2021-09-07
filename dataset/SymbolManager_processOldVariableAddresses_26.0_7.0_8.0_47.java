private void processOldVariableAddresses(TaskMonitor monitor)
			throws IOException, CancelledException {

		monitor.setMessage("Upgrading Variable Symbols...");
		monitor.initialize(adapter.getSymbolCount());
		int cnt = 0;

		Table table = adapter.getTable();

		RecordIterator symbolRecordIterator = adapter.getSymbols();
		while (symbolRecordIterator.hasNext()) {
			monitor.checkCanceled();
			monitor.setProgress(++cnt);
			Record rec = symbolRecordIterator.next();
			long addr = rec.getLongValue(SymbolDatabaseAdapter.SYMBOL_ADDR_COL);
			Address oldAddress = addrMap.decodeAddress(addr);
			if (!(oldAddress instanceof OldGenericNamespaceAddress)) {
				continue; // added by function manager upgrade
			}
			byte typeID = rec.getByteValue(SymbolDatabaseAdapter.SYMBOL_TYPE_COL);
			SymbolType type = SymbolType.getSymbolType(typeID);
			if (type != SymbolType.LOCAL_VAR && type != SymbolType.PARAMETER &&
				type != SymbolType.GLOBAL_VAR) {
				continue;
			}

			Address storageAddr = oldAddress.getNewAddress(oldAddress.getOffset());

			// move variable references - eliminate variable symbol bindings which are no longer supported
			refManager.moveReferencesTo(oldAddress, storageAddr, monitor);

			try {
				Address variableAddr = getUpgradedVariableAddress(storageAddr,
					rec.getLongValue(SymbolDatabaseAdapter.SYMBOL_DATA1_COL));

				// fix symbol address
				rec.setLongValue(SymbolDatabaseAdapter.SYMBOL_ADDR_COL,
					addrMap.getKey(variableAddr, true));
				table.putRecord(rec); // symbol key is preserved
			}
			catch (InvalidInputException e) {
				Symbol parent =
					getSymbol(rec.getLongValue(SymbolDatabaseAdapter.SYMBOL_PARENT_COL));
				Msg.warn(this, "Variable symbol upgrade problem: " + parent.getName() + ":" +
					rec.getString(SymbolDatabaseAdapter.SYMBOL_NAME_COL));
			}
		}
	}
public boolean createSwitchTable(Program program, Instruction start_inst, int opindex,
			boolean flagNewCode, TaskMonitor monitor) {

		Listing listing = program.getListing();

		int tableSize = getNumberAddressEntries();
		Address tableAddr = getTopAddress();

		ArrayList<AddLabelCmd> switchLabelList = new ArrayList<>();
		AddLabelCmd tableNameLabel = null;

		FlowType ftype = start_inst.getFlowType();
		String tableName = (ftype.isCall() ? "callTable" : "switchTable");

		String comment = null;
		String caseName = "case_0x";
		if (isNegativeTable()) {
			tableName = "neg_" + tableName;
			caseName = "case_n0x";
			comment = "This table is a negative switch table,\r\nit indexes from the bottom";
		}

		// if there are already mnemonic references, then the switch stmt is already done.
		if (start_inst.getMnemonicReferences().length > 0) {
			return false;
		}

		// check if the instruction block creating the switch is in an executable memory block
		boolean instrBlockExecutable = false;
		MemoryBlock instrBlock = program.getMemory().getBlock(start_inst.getMinAddress());
		if (instrBlock != null && instrBlock.isExecute()) {
			instrBlockExecutable = true;
		}

		// if any new code is found while makeing the table, must
		//    not finish making the table and analyze the code!
		boolean newCodeFound = false;

		// Set flag if instruction is not in a function.
		//   We prefer switch tables to already be in a function.
		boolean notInAFunction =
			program.getFunctionManager().getFunctionContaining(start_inst.getMinAddress()) == null;

		// only mark as new code if there is not already a table in progress here
		boolean tableInProgress = checkTableInProgress(program, tableAddr);

		// create table size dw's after the jmp
		//   (could create as an array)
		try {
			// create a case label
			Symbol curSymbol = program.getSymbolTable().getPrimarySymbol(tableAddr);
			if (curSymbol != null && curSymbol.getName().startsWith("Addr")) {
				tableNameLabel = new AddLabelCmd(tableAddr, tableName, true, SourceType.ANALYSIS);
			}
			else {
				tableNameLabel = new AddLabelCmd(tableAddr, tableName, true, SourceType.ANALYSIS);
			}

			Address lastAddress = null;
			DataType ptrDT = program.getDataTypeManager().addDataType(
				PointerDataType.getPointer(null, addrSize), null);
			for (int i = 0; i < tableSize; i++) {
				Address loc = tableAddr.add(i * addrSize);
				try {
					try {
						program.getListing().createData(loc, ptrDT, addrSize);
					}
					catch (CodeUnitInsertionException e) {
						CodeUnit cu = listing.getCodeUnitAt(loc);
						if (cu instanceof Instruction) {
							break;
						}
						if (cu == null) {
							Msg.warn(this, "Couldn't get data at ");
							cu = listing.getDefinedDataContaining(loc);
							if (cu == null || cu instanceof Instruction) {
								break;
							}
							cu = ((Data) cu).getPrimitiveAt((int) loc.subtract(cu.getMinAddress()));
							if (cu == null) {
								break;
							}
						}
						if (!((Data) cu).isPointer()) {
							listing.clearCodeUnits(loc, loc.add(addrSize - 1), false);
							program.getListing().createData(loc, ptrDT, addrSize);
						}
					}
				}
				catch (CodeUnitInsertionException e) {
				}
				Data data = program.getListing().getDataAt(loc);
				if (data == null) {
					continue;
				}
				Address target = ((Address) data.getValue());
				if (target == null) {
					continue;
				}

				// make sure the pointer created is the same as the table target
				Address tableTarget = tableElements[i];
				if (tableTarget != null && !target.equals(tableTarget)) {
					data.removeValueReference(target);
					data.addValueReference(tableTarget, RefType.DATA);
					target = tableTarget;
				}

				// Don't allow the targets of the switch to vary widely
				MemoryBlock thisBlock = program.getMemory().getBlock(target);
				if (lastAddress != null) {
					try {
						long diff = lastAddress.subtract(target);
						if (diff > 1024 * 128) {
							break;
						}
					}
					catch (IllegalArgumentException e) {
						break;
					}
					MemoryBlock lastBlock = program.getMemory().getBlock(lastAddress);

					if (lastBlock == null || !lastBlock.equals(thisBlock)) {
						break;
					}
				}
				lastAddress = target;

				// check that the block we are in and the block targetted is executable
				if (instrBlockExecutable && thisBlock != null && !thisBlock.isExecute()) {
					break;
				}
				// disassemble the case
				if (program.getListing().getInstructionAt(target) == null || notInAFunction) {
					if (!tableInProgress) {
						newCodeFound = true;
					}
				}

				if (!flagNewCode || !newCodeFound) {
					// create a case label
					if (!ftype.isCall()) {
						AddLabelCmd lcmd = new AddLabelCmd(target,
							caseName + Integer.toHexString(i), true, SourceType.ANALYSIS);
						switchLabelList.add(lcmd);
					}

					// add a reference to the case
					start_inst.addMnemonicReference(target, ftype, SourceType.ANALYSIS);
					//program.getReferenceManager().addMemReference(start_inst.getMinAddress(), target, ftype, false, CodeUnit.MNEMONIC);
				}

				disassembleTarget(program, target, monitor);
			}

			// if we are in a function, fix up it's body
			if (!ftype.isCall()) {
				fixupFunctionBody(program, start_inst, monitor);
			}
		}
		catch (DataTypeConflictException e1) {
			return false;
		}

		// create the index array if this table has one
		if (getIndexLength() > 0) {
			createTableIndex(program);
		}

		if (comment != null) {
			program.getListing().setComment(topAddress, CodeUnit.EOL_COMMENT, comment);
		}

		if (flagNewCode && newCodeFound) {
			// make sure we didn't get any references on the mnemonic
			//  since more code must be found
			Reference refs[] = start_inst.getMnemonicReferences();
			for (Reference ref : refs) {
				start_inst.removeMnemonicReference(ref.getToAddress());
			}
			setTableInProgress(program, tableAddr);
			return true;
		}

		// get rid of the bookmark
		// TODO: this is probably not the best use of bookmarks to signal that the
		//       creation of a switch table is in progress.
		clearTableInProgress(program, tableAddr);

		// label the table if necessary
		labelTable(program, start_inst, switchLabelList, tableNameLabel);

		return false;
	}
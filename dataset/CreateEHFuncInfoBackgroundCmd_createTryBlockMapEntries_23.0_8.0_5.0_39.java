private boolean createTryBlockMapEntries() throws CancelledException {
		monitor.setMessage("Creating TryBlockMap");
		monitor.checkCanceled();

		Address compAddress;
		Address tryBlockMapAddress;
		int tryBlockCount;
		try {
			compAddress = model.getComponentAddressOfTryBlockMapAddress();
			tryBlockMapAddress = model.getTryBlockMapAddress();
			tryBlockCount = model.getTryBlockCount();
		}
		catch (InvalidDataTypeException e) {
			throw new AssertException(e); // Shouldn't happen. create...() is only called if model is valid.
		}

		if (tryBlockMapAddress == null || tryBlockCount == 0) {
			return true; // No try block info to create.
		}

		EHTryBlockModel tryBlockModel;
		try {
			tryBlockModel = model.getTryBlockModel();
		}
		catch (InvalidDataTypeException e) {
			throw new AssertException(e); // Shouldn't happen. create...() is only called if model is valid.
		}
		try {
			tryBlockModel.validate();
		}
		catch (InvalidDataTypeException e1) {
			handleErrorMessage(model.getProgram(), tryBlockModel.getName(), tryBlockMapAddress,
				compAddress, e1);
			return false;
		}

		CreateEHTryBlockMapBackgroundCmd cmd =
			new CreateEHTryBlockMapBackgroundCmd(tryBlockModel, applyOptions);
		return cmd.applyTo(model.getProgram(), monitor);
	}
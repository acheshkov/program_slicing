private static boolean addRegisterUsage(Program program, HashSet<Varnode> setAtStartRegisters,
			HashSet<Varnode> setRegisters, HashSet<Varnode> usedRegisters, PcodeOp pcode,
			boolean allow8bitNonUse) {
		int opcode = pcode.getOpcode();
		Varnode output = pcode.getOutput();

		// copying from a memory address is an unknown input
		if (opcode == PcodeOp.COPY) {
			if (output.isAddress()) {
				return false;
			}
			// if input same as output, is a NOP pcode op
			if (output.equals(pcode.getInput(0))) {
				return true;
			}
		}

		Varnode[] inputs = pcode.getInputs();
		for (Varnode input : inputs) {
			// if scalar, is OK
			// if memory load, OK
			// if register, must be on the set list
			Varnode inVarnode = input;
			if (inVarnode.isRegister()) {
				if ((!allow8bitNonUse || inVarnode.getSize() > 1) &&
					!containsRegister(program, setRegisters, inVarnode) &&
					!containsRegister(program, setAtStartRegisters, inVarnode)) {
					return false;
				}
				// it doesn't count as use if the sizes aren't equivalent
				//  some instructions set flags as a side-effect
				if (output == null || output.getSize() >= inVarnode.getSize()) {
					usedRegisters.add(inVarnode);
				}
			}
		}

		// if address, bad
		// if big enough register, must be on set list
		if (output != null && output.isRegister()) {
			if (!allow8bitNonUse || output.getSize() > 1) {
				setRegisters.add(output);
				// we set it, now it needs a new use!
				usedRegisters.remove(output);
			}
		}
		return true;
	}
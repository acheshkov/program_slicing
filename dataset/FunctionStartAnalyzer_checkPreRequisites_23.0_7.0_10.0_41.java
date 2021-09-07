protected boolean checkPreRequisites(Program program, Address addr) {
			/**
			 * If the match's mark point occurs in undefined data, schedule disassembly
			 * and a function start at that address. If the match's mark point occurs at an instruction, but that
			 * instruction isn't in a function body, schedule a function start at that address
			 */
			if (validFunction) {
				Function func = program.getFunctionManager().getFunctionAt(addr);
				if (func == null) {
					postreqFailedResult.add(addr);
					// Drop a property breadcrumb to make sure only those functions that could match are checked.
					potentialMatchAddressSetPropertyMap.add(addr, addr);
					return false;
				}
			}

			if (!checkAfterName(program, addr)) {
				postreqFailedResult.add(addr);
				return false;
			}

			// do we require some number of valid instructions
			if (validcode != 0) {
				PseudoDisassembler pseudoDisassembler = new PseudoDisassembler(program);
				PseudoDisassemblerContext pcont =
					new PseudoDisassemblerContext(program.getProgramContext());
				setDisassemblerContext(program, pcont);
				boolean isvalid = false;
				if (validcode == -1) {
					isvalid = pseudoDisassembler.checkValidSubroutine(addr, pcont, true, true);
				}
				else {
					pseudoDisassembler.setMaxInstructions(validcode);
					isvalid = pseudoDisassembler.checkValidSubroutine(addr, pcont, true, false);
				}
				if (!isvalid) {
					return false;
				}
			}

			return true;
		}
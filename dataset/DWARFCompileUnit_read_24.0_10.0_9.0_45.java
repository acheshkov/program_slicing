public static DWARFCompileUnit read(DIEAggregate diea, BinaryReader lineReader)
			throws IOException, DWARFException {
		if (diea.getTag() != DWARFTag.DW_TAG_compile_unit) {
			throw new IOException("Expecting a DW_TAG_compile_unit DIE, found " + diea.getTag());
		}

		String name = diea.getString(DWARFAttribute.DW_AT_name, null);
		String producer = diea.getString(DWARFAttribute.DW_AT_producer, null);
		String comp_dir = diea.getString(DWARFAttribute.DW_AT_comp_dir, null);

		Number high_pc = null, low_pc = null, language = null, stmt_list = null;
		if (diea.hasAttribute(DWARFAttribute.DW_AT_low_pc)) {
			low_pc = diea.getLowPC(0);
		}

		if (diea.hasAttribute(DWARFAttribute.DW_AT_high_pc)) {
			high_pc = diea.getHighPC();
		}

		if (diea.hasAttribute(DWARFAttribute.DW_AT_language)) {
			language = diea.getUnsignedLong(DWARFAttribute.DW_AT_language, -1);
		}

		// DW_AT_stmt_list can be const or ptr form types.
		if (diea.hasAttribute(DWARFAttribute.DW_AT_stmt_list)) {
			stmt_list = diea.getUnsignedLong(DWARFAttribute.DW_AT_stmt_list, -1);
		}

		DWARFIdentifierCase identifier_case = null;
		if (diea.hasAttribute(DWARFAttribute.DW_AT_identifier_case)) {
			identifier_case = DWARFIdentifierCase.find(
				diea.getUnsignedLong(DWARFAttribute.DW_AT_identifier_case, -1));
		}

		boolean hasDWO = diea.hasAttribute(DWARFAttribute.DW_AT_GNU_dwo_id) &&
			diea.hasAttribute(DWARFAttribute.DW_AT_GNU_dwo_name);

		DWARFLine line = null;
		if (stmt_list != null && lineReader != null) {
			lineReader.setPointerIndex(stmt_list.longValue());
			line = new DWARFLine(lineReader);
		}

		return new DWARFCompileUnit(name, producer, comp_dir, low_pc, high_pc, language, stmt_list,
			identifier_case, hasDWO, line);
	}
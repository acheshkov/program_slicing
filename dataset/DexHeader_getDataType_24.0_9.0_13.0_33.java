public DataType getDataType(Program program, short typeShort) {
		int typeId = typeShort & 0xffff;
		if (typeId < 0 || typeId >= typeIdsSize) {
			return null;
		}
		DataType res;
		synchronized (typeXref) {
			res = typeXref.get(typeId);
			if (res == null) {
				TypeIDItem typeIDItem = types.get(typeId);
				String typeString = DexUtil.convertToString(this, typeIDItem.getDescriptorIndex());
				if (typeString.length() != 0 && typeString.charAt(0) == 'L') {
					StringBuilder buffer = new StringBuilder();
					buffer.append(DexUtil.HANDLE_PATH);
					buffer.append("group").append(typeId / 100);
					buffer.append(CategoryPath.DELIMITER_CHAR);
					buffer.append("type").append(typeId);
					DataType handleType =
						program.getDataTypeManager().getDataType(buffer.toString());
					if (handleType instanceof TypeDef) {
						res = new PointerDataType(((TypeDef) handleType).getDataType(),
							program.getDataTypeManager());
					}
				}
				if (res == null) {
					res = DexUtil.toDataType(program.getDataTypeManager(), typeString);
				}
				if (res != null) {
					typeXref.put(typeId, res);
				}
			}
		}
		return res;
	}
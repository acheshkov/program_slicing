protected void populate() {
		int id = super.startTransaction("Populate");
		try {
			resolve(new ByteDataType(), null);
			resolve(new CharDataType(), null);
			resolve(new BooleanDataType(), null);
			resolve(new DoubleDataType(), null);
			resolve(new StringDataType(), null);
			resolve(new Undefined1DataType(), null);
			resolve(new Undefined2DataType(), null);
			resolve(new Undefined4DataType(), null);
			resolve(new Undefined8DataType(), null);
			resolve(new UnicodeDataType(), null);
			resolve(new VoidDataType(), null);
			resolve(new IntegerDataType(), null);
			resolve(new ShortDataType(), null);

			StructureDataType struct1 = new StructureDataType("abc", 4);
			struct1.setCategoryPath(new CategoryPath("/foo"));
			resolve(struct1, null);

			StructureDataType struct2 = new StructureDataType("abc", 4);
			struct2.setCategoryPath(new CategoryPath("/bar"));
			resolve(struct2, null);
		}
		finally {
			super.endTransaction(id, true);
		}

	}
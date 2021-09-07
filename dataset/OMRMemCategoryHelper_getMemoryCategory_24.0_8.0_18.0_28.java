public static OMRMemCategoryPointer getMemoryCategory(UDATA memoryCategory) throws CorruptDataException {
		J9PortLibraryPointer portLib = J9RASHelper.getVM(DataType.getJ9RASPointer()).portLibrary();
		OMRPortLibraryGlobalDataPointer portGlobals = portLib.omrPortLibrary().portGlobals();

		if (memoryCategory.eq(OMRMEM_CATEGORY_PORT_LIBRARY)) {
			return portGlobals.portLibraryMemoryCategory();
		} else if (J9BuildFlags.env_data64 && memoryCategory.eq(OMRMEM_CATEGORY_PORT_LIBRARY_UNUSED_ALLOCATE32_REGIONS)) {
			return getUnusedAllocate32HeapRegionsMemoryCategory(portGlobals);
		} else {
			OMRMemCategorySetPointer registeredSet = OMRMemCategorySetPointer.NULL;
			long index = 0;
			if (memoryCategory.lt(new U32(0x7FFFFFFFl))) {
				registeredSet = portGlobals.control().language_memory_categories();
				index = memoryCategory.longValue();
			} else {
				registeredSet = portGlobals.control().omr_memory_categories();
				index = (0x7FFFFFFFL & memoryCategory.longValue());
			}
			if (registeredSet.notNull()) {
				if (registeredSet.numberOfCategories().gt(index) && registeredSet.categories().at(index).notNull()) {
					return OMRMemCategoryPointer.cast(registeredSet.categories().at(index));
				} else {
					return portGlobals.unknownMemoryCategory();
				}
			} else {
				return portGlobals.unknownMemoryCategory();
			}
		}
	}
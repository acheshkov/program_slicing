@Override
    public PagedPointer alloc(long requiredMemory, DataType type, boolean initialize) {
	    return this.alloc(requiredMemory, MemoryKind.DEVICE, type, initialize);
    }
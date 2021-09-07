private void parseMemory() throws IOException {
			coreSeek(_regionOffset);
			_memoryRanges = new ArrayList();
			MemoryRange memoryRange = null;
			for (int i = 0; i < _regionCount; i++) {
				long start = coreReadInt();
				coreReadInt(); // Ignore allocationBase
				coreReadInt(); // Ignore allocationProtect
				int size = coreReadInt();
				coreReadInt(); // Ignore state
				coreReadInt(); // Ignore protect
				coreReadInt(); // Ignore type
				
				if (null == memoryRange) {
					// Allocate the first memory range starting at _dataOffset in the dump file
					memoryRange = new MemoryRange(start, _dataOffset, size);
				} else if (memoryRange.getVirtualAddress() + memoryRange.getSize() == start) {
					// Combine contiguous regions
					memoryRange = new MemoryRange(memoryRange.getVirtualAddress(),
												  memoryRange.getFileOffset(),
												  memoryRange.getSize() + size);
				} else {
					// Add the previous MemoryRange and start the next one
					_memoryRanges.add(memoryRange);
					memoryRange = new MemoryRange(start,
							  					  memoryRange.getFileOffset() + memoryRange.getSize(),
							  					  size);
				}
			}
			
			if (null != memoryRange)
				_memoryRanges.add(memoryRange);
		}
@Override
	public boolean write(T record) throws IOException {
		//check whether we need a new memory segment for the sort index
		if (this.currentSortIndexOffset > this.lastIndexEntryOffset) {
			if (memoryAvailable()) {
				this.currentSortIndexSegment = nextMemorySegment();
				this.sortIndex.add(this.currentSortIndexSegment);
				this.currentSortIndexOffset = 0;
				this.sortIndexBytes += this.segmentSize;
			} else {
				return false;
			}
		}
		
		// serialize the record into the data buffers
		try {
			this.serializer.serialize(record, this.recordCollector);
		}
		catch (EOFException e) {
			return false;
		}
		
		final long newOffset = this.recordCollector.getCurrentOffset();
		final boolean shortRecord = newOffset - this.currentDataBufferOffset < LARGE_RECORD_THRESHOLD;
		
		if (!shortRecord && LOG.isDebugEnabled()) {
			LOG.debug("Put a large record ( >" + LARGE_RECORD_THRESHOLD + " into the sort buffer");
		}
		
		// add the pointer and the normalized key
		this.currentSortIndexSegment.putLong(this.currentSortIndexOffset, shortRecord ?
				this.currentDataBufferOffset : (this.currentDataBufferOffset | LARGE_RECORD_TAG));

		if (this.numKeyBytes != 0) {
			this.comparator.putNormalizedKey(record, this.currentSortIndexSegment, this.currentSortIndexOffset + OFFSET_LEN, this.numKeyBytes);
		}
		
		this.currentSortIndexOffset += this.indexEntrySize;
		this.currentDataBufferOffset = newOffset;
		this.numRecords++;
		return true;
	}
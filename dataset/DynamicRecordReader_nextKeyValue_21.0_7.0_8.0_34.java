@Override
  public boolean nextKeyValue()
      throws IOException, InterruptedException {

    if (chunk == null) {
      if (LOG.isDebugEnabled())
        LOG.debug(taskId + ": RecordReader is null. No records to be read.");
      return false;
    }

    if (chunk.getReader().nextKeyValue()) {
      ++numRecordsProcessedByThisMap;
      return true;
    }

    if (LOG.isDebugEnabled())
      LOG.debug(taskId + ": Current chunk exhausted. " +
                         " Attempting to pick up new one.");

    chunk.release();
    timeOfLastChunkDirScan = System.currentTimeMillis();
    isChunkDirAlreadyScanned = false;
    
    chunk = chunkContext.acquire(taskAttemptContext);

    if (chunk == null) return false;

    if (chunk.getReader().nextKeyValue()) {
      ++numRecordsProcessedByThisMap;
      return true;
    }
    else {
      return false;
    }
  }
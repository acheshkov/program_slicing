@Override
	public void run(SourceFunction.SourceContext<TimestampedFileInputSplit> context) throws Exception {
		Path p = new Path(path);
		FileSystem fileSystem = FileSystem.get(p.toUri());
		if (!fileSystem.exists(p)) {
			throw new FileNotFoundException("The provided file path " + path + " does not exist.");
		}

		checkpointLock = context.getCheckpointLock();
		switch (watchType) {
			case PROCESS_CONTINUOUSLY:
				while (isRunning) {
					synchronized (checkpointLock) {
						monitorDirAndForwardSplits(fileSystem, context);
					}
					Thread.sleep(interval);
				}

				// here we do not need to set the running to false and the
				// globalModificationTime to Long.MAX_VALUE because to arrive here,
				// either close() or cancel() have already been called, so this
				// is already done.

				break;
			case PROCESS_ONCE:
				synchronized (checkpointLock) {

					// the following check guarantees that if we restart
					// after a failure and we managed to have a successful
					// checkpoint, we will not reprocess the directory.

					if (globalModificationTime == Long.MIN_VALUE) {
						monitorDirAndForwardSplits(fileSystem, context);
						globalModificationTime = Long.MAX_VALUE;
					}
					isRunning = false;
				}
				break;
			default:
				isRunning = false;
				throw new RuntimeException("Unknown WatchType" + watchType);
		}
	}
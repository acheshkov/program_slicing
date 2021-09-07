private void checkOldProperties(int openMode, TaskMonitor monitor)
			throws IOException, VersionException {
		Record record = table.getRecord(new StringField(EXECUTE_PATH));
		if (record != null) {
			if (openMode == READ_ONLY) {
				return; // not important, get on path or format will return "unknown"
			}
			if (openMode != UPGRADE) {
				throw new VersionException(true);
			}
			Options pl = getOptions(PROGRAM_INFO);
			String value = record.getString(0);
			pl.setString(EXECUTABLE_PATH, value);
			table.deleteRecord(record.getKeyField());
			record = table.getRecord(new StringField(EXECUTE_FORMAT));
			if (record != null) {
				pl.setString(EXECUTABLE_FORMAT, value);
				table.deleteRecord(record.getKeyField());
			}
		}
		int storedVersion = getStoredVersion();
		if (storedVersion < ANALYSIS_OPTIONS_MOVED_VERSION) {
			if (openMode == READ_ONLY) {
				return;
			}
			if (openMode != UPGRADE) {
				throw new VersionException(true);
			}
			Options oldList = getOptions("Analysis");
			for (String propertyName : oldList.getOptionNames()) {
				oldList.removeOption(propertyName);
			}
		}
		if (storedVersion < METADATA_ADDED_VERSION) {
			if (openMode == READ_ONLY) {
				return;
			}
			if (openMode != UPGRADE) {
				throw new VersionException(true);
			}
		}

	}
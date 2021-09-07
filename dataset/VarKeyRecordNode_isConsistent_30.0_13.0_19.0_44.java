@Override
	public boolean isConsistent(String tableName, TaskMonitor monitor)
			throws IOException, CancelledException {
		boolean consistent = true;
		Field prevKey = null;
		for (int i = 0; i < keyCount; i++) {
			// Compare each key entry with the previous key
			Field key = getKey(i);
			if (i != 0) {
				if (key.compareTo(prevKey) <= 0) {
					consistent = false;
					logConsistencyError(tableName, "key[" + i + "] <= key[" + (i - 1) + "]", null);
					Msg.debug(this, "  key[" + i + "].minKey = " + key);
					Msg.debug(this, "  key[" + (i - 1) + "].minKey = " + prevKey);
				}
			}
			prevKey = key;
		}

		if ((parent == null || parent.isLeftmostKey(getKey(0))) && getPreviousLeaf() != null) {
			consistent = false;
			logConsistencyError(tableName, "previous-leaf should not exist", null);
		}

		VarKeyRecordNode node = getNextLeaf();
		if (node != null) {
			if (parent == null || parent.isRightmostKey(getKey(0))) {
				consistent = false;
				logConsistencyError(tableName, "next-leaf should not exist", null);
			}
			else {
				VarKeyRecordNode me = node.getPreviousLeaf();
				if (me != this) {
					consistent = false;
					logConsistencyError(tableName, "next-leaf is not linked to this leaf", null);
				}
			}
		}
		else if (parent != null && !parent.isRightmostKey(getKey(0))) {
			consistent = false;
			logConsistencyError(tableName, "this leaf is not linked to next-leaf", null);
		}

		return consistent;
	}
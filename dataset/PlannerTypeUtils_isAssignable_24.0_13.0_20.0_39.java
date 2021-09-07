public static boolean isAssignable(LogicalType t1, LogicalType t2) {
		// Soft check for CharType, it is converted to String TypeInformation and loose char information.
		if (t1.getTypeRoot().getFamilies().contains(CHARACTER_STRING) &&
				t2.getTypeRoot().getFamilies().contains(CHARACTER_STRING)) {
			return true;
		}
		if (t1.getTypeRoot().getFamilies().contains(BINARY_STRING) &&
				t2.getTypeRoot().getFamilies().contains(BINARY_STRING)) {
			return true;
		}
		if (t1.getTypeRoot() != t2.getTypeRoot()) {
			return false;
		}

		switch (t1.getTypeRoot()) {
			// only support precisions for DECIMAL, TIMESTAMP_WITHOUT_TIME_ZONE, TIMESTAMP_WITH_LOCAL_TIME_ZONE
			// still consider precision for others (e.g. TIME).
			// TODO: add other precision types here in the future
			case DECIMAL:
			case TIMESTAMP_WITHOUT_TIME_ZONE:
			case TIMESTAMP_WITH_LOCAL_TIME_ZONE:
				return true;
			default:
				if (t1.getChildren().isEmpty()) {
					return t1.copy(true).equals(t2.copy(true));
				} else {
					List<LogicalType> children1 = t1.getChildren();
					List<LogicalType> children2 = t2.getChildren();
					if (children1.size() != children2.size()) {
						return false;
					}
					for (int i = 0; i < children1.size(); i++) {
						if (!isAssignable(children1.get(i), children2.get(i))) {
							return false;
						}
					}
					return true;
				}
		}
	}
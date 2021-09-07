private static void readDecimalColumn(Object[] vals, int fieldIdx, DecimalColumnVector vector, int childCount) {

		if (vector.isRepeating) { // fill complete column with first value
			if (vector.isNull[0]) {
				// fill vals with null values
				fillColumnWithRepeatingValue(vals, fieldIdx, null, childCount);
			} else {
				// read repeating non-null value by forwarding call
				readNonNullDecimalColumn(vals, fieldIdx, vector, childCount);
			}
		} else {
			boolean[] isNullVector = vector.isNull;
			if (fieldIdx == -1) { // set as an object
				for (int i = 0; i < childCount; i++) {
					if (isNullVector[i]) {
						vals[i] = null;
					} else {
						vals[i] = readBigDecimal(vector.vector[i]);
					}
				}
			} else { // set as a field of Row
				Row[] rows = (Row[]) vals;
				for (int i = 0; i < childCount; i++) {
					if (isNullVector[i]) {
						rows[i].setField(fieldIdx, null);
					} else {
						rows[i].setField(fieldIdx, readBigDecimal(vector.vector[i]));
					}
				}
			}
		}
	}
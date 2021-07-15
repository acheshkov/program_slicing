		void removeElementFromFilters(int index) {
			if (filteredIndexes != null) {
				int location = Arrays.binarySearch(filteredIndexes, index);
				if (location >= 0) {
					// remove a filtered item
					if (filteredIndexes.length == 1) {
						// only filtered item
						filteredIndexes = null;
						filteredElements = null;
					} else {
						int[] next = new int[filteredIndexes.length - 1];
						Object[] filt = new Object[next.length];
						if (location == 0) {
							// first
							System.arraycopy(filteredIndexes, 1, next, 0, next.length);
							System.arraycopy(filteredElements, 1, filt, 0, filt.length);
						} else if (location == (filteredIndexes.length - 1)) {
							// last
							System.arraycopy(filteredIndexes, 0, next, 0, next.length);
							System.arraycopy(filteredElements, 0, filt, 0, filt.length);
						} else {
							// middle
							System.arraycopy(filteredIndexes, 0, next, 0, location);
							System.arraycopy(filteredElements, 0, filt, 0, location);
							System.arraycopy(filteredIndexes, location + 1, next, location, next.length - location);
							System.arraycopy(filteredElements, location + 1, filt, location, filt.length - location);
						}
						filteredIndexes = next;
						filteredElements = filt;
					}
				} else {
					location = 0 - (location + 1);
				}
				if (filteredIndexes != null) {
					// decrement remaining indexes
					for (int i = location; i < filteredIndexes.length; i ++) {
						filteredIndexes[i]--;
					}
				}
			}
		}
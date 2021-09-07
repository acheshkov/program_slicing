void removeUpdateUpdate(DocumentEvent evt) {
        // Check whether removal would affect any contained text regions
        // and if so remove their associated text sync groups.
        int minGroupIndex = Integer.MAX_VALUE;
        int removeStartOffset = evt.getOffset();
        int removeEndOffset = removeStartOffset + evt.getLength();
        List<TextRegion<?>> regions = rootRegion.regions();
        int index = findRegionInsertIndex(regions, removeStartOffset);
        if (index > 0) { // Check whether region at index-1 is not affected by the removal
            TextRegion<?> region = regions.get(index - 1);
            minGroupIndex = findMinGroupIndex(minGroupIndex, region, removeStartOffset, removeEndOffset);
        }
        for (;index < regions.size(); index++) {
            TextRegion<?> region = regions.get(index);
            if (region.startOffset() >= removeEndOffset) {
                break;
            }
            minGroupIndex = findMinGroupIndex(minGroupIndex, region, removeStartOffset, removeEndOffset);
        }
        if (minGroupIndex != Integer.MAX_VALUE) {
            int removeCount = editGroups.size() - minGroupIndex;
            if (LOG.isLoggable(Level.FINE)) {
                StringBuilder sb = new StringBuilder(100);
                sb.append("removeUpdateUpdate(): Text remove <").append(removeStartOffset);
                sb.append(",").append(removeEndOffset).append(">.\n  Removing GROUPS <");
                sb.append(minGroupIndex).append(",").append(editGroups.size()).append(">\n");
                LOG.fine(sb.toString());
            }
            releaseLastGroups(removeCount);
        }
    }
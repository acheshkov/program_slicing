private void copyGapInsideGroup(LayoutInterval gap, int gapSize, LayoutInterval group, int alignment) {
        assert gap.isEmptySpace() && (alignment == LEADING || alignment == TRAILING);

        if (alignment == LEADING)
            gapSize = -gapSize;

        group.getCurrentSpace().positions[dimension][alignment] += gapSize;

        List<LayoutInterval> originalGroup = new ArrayList<LayoutInterval>(group.getSubIntervalCount());
        for (Iterator<LayoutInterval> it=group.getSubIntervals(); it.hasNext(); ) {
            originalGroup.add(it.next());
        }

        for (LayoutInterval sub : originalGroup) {
            LayoutInterval gapClone = LayoutInterval.cloneInterval(gap, null);
            if (sub.isSequential()) {
                sub.getCurrentSpace().positions[dimension][alignment] += gapSize;
                int index = alignment == LEADING ? 0 : sub.getSubIntervalCount();
                operations.insertGapIntoSequence(gapClone, sub, index, dimension);
            }
            else {
                LayoutInterval seq = new LayoutInterval(SEQUENTIAL);
                seq.getCurrentSpace().set(dimension, sub.getCurrentSpace());
                seq.getCurrentSpace().positions[dimension][alignment] += gapSize;
                seq.setAlignment(sub.getRawAlignment());
                layoutModel.addInterval(seq, group, layoutModel.removeInterval(sub));
                layoutModel.setIntervalAlignment(sub, DEFAULT);
                layoutModel.addInterval(sub, seq, 0);
                layoutModel.addInterval(gapClone, seq, alignment == LEADING ? 0 : 1);
            }
        }
    }
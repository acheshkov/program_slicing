public void adjustComponentAlignment(LayoutComponent comp, int dimension, int alignment) {
        if (logTestCode()) {
            testCode.add("// > ADJUST COMPONENT ALIGNMENT"); //NOI18N
            testCode.add("{"); //NOI18N
            testCode.add("LayoutComponent comp = lm.getLayoutComponent(\"" + comp.getId() + "\");"); //NOI18N
            testCode.add("int dimension = " + dimension + ";");	    //NOI18N
            testCode.add("int alignment = " + alignment + ";");          //NOI18N 
            testCode.add("ld.adjustComponentAlignment(comp, dimension, alignment);"); //NOI18N
            testCode.add("}"); //NOI18N
        }
        LayoutInterval interval = comp.getLayoutInterval(dimension);
        
        // Skip non-resizable groups
        LayoutInterval parent = interval.getParent();
        while (parent != null) {
            if (!LayoutInterval.canResize(parent)) {
                interval = parent;
            }
            parent = parent.getParent();
        }
        assert !LayoutInterval.wantResize(interval);
        
        parent = interval.getParent();
        while (parent != null) {
            if (parent.isParallel()) {
                if (LayoutInterval.wantResize(parent) && !LayoutInterval.wantResize(interval)) {
                    int alg = interval.getAlignment();
                    if (alg != alignment) {
                        // add fixed supporting gap in the anchor direction, and change alignment
                        int pos = parent.getCurrentSpace().positions[dimension][alignment];
                        int size = (pos - interval.getCurrentSpace().positions[dimension][alignment]) * (alignment == LEADING ? -1 : 1);
                        if (size > 0) {
                            LayoutInterval gap = new LayoutInterval(SINGLE);
                            gap.setSize(size);
                            operations.insertGap(gap, interval, pos, dimension, alignment);
                        }
                        layoutModel.setIntervalAlignment(interval, alignment);
                    }
                    break; // assuming the anchor was clear before, so we need only one correction
                }
            } else { // in sequence
                // first eliminate resizing gaps in the desired anchor direction
                boolean before = true;
                boolean seqWasResizing = false;
                boolean otherSidePushing = false;
                for (int i=0; i<parent.getSubIntervalCount(); i++) {
                    LayoutInterval li = parent.getSubInterval(i);
                    if (li == interval) {
                        before = false;
                    } else if (LayoutInterval.wantResize(li)) {
                        if ((before && (alignment == LEADING)) || (!before && (alignment == TRAILING))) {
                            assert li.isEmptySpace();
                            int expCurrentSize = NOT_EXPLICITLY_DEFINED;
                            if (li.getDiffToDefaultSize() != 0 && li.getPreferredSize() <= 0) {
                                expCurrentSize = LayoutInterval.getCurrentSize(li, dimension);
                            }
                            operations.setIntervalResizing(li, false);
                            if (expCurrentSize > 0) {
                                operations.resizeInterval(li, expCurrentSize);
                            } else if (operations.eliminateUnwantedZeroGap(li)) {
                                i--;
                            }
                            seqWasResizing = true;
                        } else {
                            otherSidePushing = true;
                        }
                    }
                }
                // second, if needed make a resizing gap in the other direction
                if (!otherSidePushing && parent.getAlignment() != alignment
                    && (seqWasResizing
                        || (!LayoutInterval.wantResize(parent)
                            && LayoutInterval.wantResize(parent.getParent())))) {
                    layoutModel.setIntervalAlignment(parent, alignment);
                    boolean insertGap = false;
                    int index = parent.indexOf(interval);
                    if (alignment == LEADING) {
                        if (parent.getSubIntervalCount() <= index+1) {
                            insertGap = true;
                            index = -1;
                        } else {
                            index++;
                            LayoutInterval candidate = parent.getSubInterval(index);
                            if (candidate.isEmptySpace()) {
                                operations.setIntervalResizing(candidate, true);
                            } else {
                                insertGap = true;
                            }
                        }
                    } else {
                        assert (alignment == TRAILING);
                        if (index == 0) {
                            insertGap = true;
                        } else {                            
                            LayoutInterval candidate = parent.getSubInterval(index-1);
                            if (candidate.isEmptySpace()) {
                                operations.setIntervalResizing(candidate, true);
                            } else {
                                insertGap = true;
                            }
                        }
                    }
                    if (insertGap) { // could not change existing gap, adding new
                        LayoutInterval gap = new LayoutInterval(SINGLE);
                        operations.setIntervalResizing(gap, true);
                        layoutModel.setIntervalSize(gap, 0, 0, gap.getMaximumSize());
                        layoutModel.addInterval(gap, parent, index);
                        operations.optimizeGaps2(parent.getParent(), dimension);
                        parent = interval.getParent();
                    }
                    if (!seqWasResizing) { // also may need a supporting gap in the anchor direction
                        int pos = parent.getParent().getCurrentSpace().positions[dimension][alignment];
                        int size = (pos - parent.getCurrentSpace().positions[dimension][alignment]) * (alignment == LEADING ? -1 : 1);
                        if (size > 0) {
                            LayoutInterval gap = new LayoutInterval(SINGLE);
                            gap.setSize(size);
                            operations.insertGap(gap, parent, pos, dimension, alignment);
                        }
                    }
                    break; // assuming the anchor was clear before, so we need only one correction
                }
            }
            interval = parent;
            parent = parent.getParent();
        }
        visualStateUpToDate = false;
        updateDataAfterBuild = true;
        if (logTestCode()) {
            testCode.add("// < ADJUST COMPONENT ALIGNMENT"); //NOI18N
	}
    }
private void checkRootForNextTo(LayoutInterval layoutRoot, int alignment) {
        assert alignment == LayoutRegion.ALL_POINTS || alignment == LEADING || alignment == TRAILING;

        if (operation == RESIZING && isValidNextToResizing(layoutRoot, alignment) != 1)
            return;

        LayoutRegion rootSpace = layoutRoot.getCurrentSpace();

        for (int i = LEADING; i <= TRAILING; i++) {
            if (alignment == LayoutRegion.ALL_POINTS || alignment == i) {
                int distance = LayoutRegion.distance(rootSpace, movingSpace,
                                                     dimension, i, i);
                assert distance != LayoutRegion.UNKNOWN;
                if (snapping) {
                    // PENDING consider the resulting interval when moving more components
                    int[] pads = findPaddings(null, movingComponents[0].getLayoutInterval(dimension), null, dimension, i);
                    int pad = (pads != null && pads.length > 0) ? pads[0] : 0;
                    distance += (i == LEADING ? -pad : pad);
                }

                if (!snapping || Math.abs(distance) < SNAP_DISTANCE) {
                    PositionDef bestSoFar = findingsNextTo[dimension][i];
                    assert !bestSoFar.isSet();
                    bestSoFar.interval = layoutRoot;
                    bestSoFar.alignment = i;
                    bestSoFar.distance = distance;
                    bestSoFar.nextTo = true;
                    bestSoFar.snapped = snapping && Math.abs(distance) < SNAP_DISTANCE;
                    bestSoFar.paddingType = null;
                    bestSoFar.paddingSizes = null;
                }
            }
        }
    }
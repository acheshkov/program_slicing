    public boolean reportRecordedErrors(Scope scope, int mergedStatus) {
        FakedTrackingVariable current = this;
        while (current.globalClosingState == 0) {
            current = current.innerTracker;
            if (current == null) {
                // no relevant state found -> report:
                reportError(scope.problemReporter(), null, mergedStatus);
                return true;
            }
        }
        boolean hasReported = false;
        if (this.recordedLocations != null) {
            Iterator locations = this.recordedLocations.entrySet().iterator();
            int reportFlags = 0;
            while (locations.hasNext()) {
                Map.Entry entry = (Entry) locations.next();
                reportFlags |= reportError(scope.problemReporter(), (ASTNode)entry.getKey(), ((Integer)entry.getValue()).intValue());
                hasReported = true;
            }
            if (reportFlags != 0) {
                // after all locations have been reported, mark as reported to prevent duplicate report via an outer wrapper
                current = this;
                do {
                    current.globalClosingState |= reportFlags;
                } while ((current = current.innerTracker) != null);
            }
        }
        return hasReported;
    }
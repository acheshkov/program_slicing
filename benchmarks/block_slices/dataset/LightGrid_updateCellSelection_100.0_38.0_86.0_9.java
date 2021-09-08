@Nullable
    private Event updateCellSelection(
            @NotNull GridPos newCell,
            int stateMask,
            boolean dragging,
            boolean reverseDuplicateSelections,
            EventSource eventSource)
    {
        return updateCellSelection(Collections.singletonList(newCell), stateMask, dragging, reverseDuplicateSelections, eventSource);
    }
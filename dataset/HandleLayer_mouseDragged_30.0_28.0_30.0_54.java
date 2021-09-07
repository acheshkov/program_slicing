@Override
    public void mouseDragged(MouseEvent e) {
        if (formDesigner.getDesignerMode() != FormDesigner.MODE_SELECT) {
            return; // dragging makes sense only in selection mode
        }
        Point p = e.getPoint();
        if (lastMousePosition != null) {
            lastXPosDiff = p.x - lastMousePosition.x;
            lastYPosDiff = p.y - lastMousePosition.y;
        }

        if (!draggingEnded && !anyDragger() && lastLeftMousePoint != null) { // no dragging yet
            if (!viewOnly
                    && !e.isControlDown() && !e.isMetaDown() && (!e.isShiftDown() || e.isAltDown())
                    && (resizeType != 0 || lastLeftMousePoint.distance(p) > 6)) {
                // start component dragging
                RADVisualComponent[] draggedComps =
                    (resizeType & DESIGNER_RESIZING) == 0 ? getComponentsToDrag() :
                    new RADVisualComponent[] { formDesigner.getTopDesignComponent() };
                if (draggedComps != null) {
                    if (resizeType == 0) {
                        draggedComponent = new ExistingComponentDrag(
                            draggedComps, lastLeftMousePoint, e.getModifiers());
                    } else  {
                        draggedComponent = new ResizeComponentDrag(
                            draggedComps, lastLeftMousePoint, resizeType);
                    }
                }
            }
            if (draggedComponent == null // component dragging has not started
                    && lastLeftMousePoint.distance(p) > 4
                    && !e.isAltDown() && !e.isControlDown() && !e.isMetaDown()) {
                // check for possible selection dragging
                RADComponent topComp = formDesigner.getTopDesignComponent();
                RADComponent comp = getMetaComponentAt(lastLeftMousePoint, COMP_DEEPEST);
                if (topComp != null
                    && (e.isShiftDown() || comp == null || comp == topComp || comp.getParentComponent() == null)) {
                    // start selection dragging
                    selectionDragger = new SelectionDragger(lastLeftMousePoint);
                }
            }
        }

        if (draggedComponent != null) {
            draggedComponent.move(e);
            highlightPanel(e, false);
            repaint();
        } else if (selectionDragger != null) {
            selectionDragger.drag(p);
            repaint();
        }

        lastMousePosition = p;
        e.consume();
    }
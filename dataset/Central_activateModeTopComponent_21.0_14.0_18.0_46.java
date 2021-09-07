public void activateModeTopComponent(ModeImpl mode, TopComponent tc) {
        if(!getModeOpenedTopComponents(mode).contains(tc)) {
            return;
        }
        
        ModeImpl oldActiveMode = getActiveMode();
        //#45650 -some API users call the activation all over again all the time on one item.
        // improve performance for such cases.
        if (oldActiveMode != null && oldActiveMode.equals(mode)) {
            if (tc != null && tc.equals(model.getModeSelectedTopComponent(mode))) {
                // #82385, #139319 do repeat activation if focus is not
                // owned by tc to be activated
                Component fOwn = KeyboardFocusManager.getCurrentKeyboardFocusManager().
                        getFocusOwner();
                if (fOwn != null && SwingUtilities.isDescendingFrom(fOwn, tc)) {
                    //#70173 - activation request came probably from a sliding
                    //window in 'hover' mode, so let's hide it
                    slideOutSlidingWindows( mode );
                    return;
                }
            }
        }
        model.setActiveMode(mode);
        model.setModeSelectedTopComponent(mode, tc);
        
        if(isVisible()) {
            viewRequestor.scheduleRequest(new ViewRequest(mode, 
                View.CHANGE_TOPCOMPONENT_ACTIVATED, null, tc));

            //restore floating windows if iconified
            if( mode.getState() == Constants.MODE_STATE_SEPARATED ) {
                Frame frame = (Frame) SwingUtilities.getAncestorOfClass(Frame.class, tc);
                if( null != frame && frame != WindowManagerImpl.getInstance().getMainWindow()
                        && (frame.getExtendedState() & Frame.ICONIFIED) > 0 ) {
                    frame.setExtendedState(frame.getExtendedState() - Frame.ICONIFIED );
                }
            }
        }
        
        // Notify registry.
        WindowManagerImpl.notifyRegistryTopComponentActivated(tc);
        
        if(oldActiveMode != mode) {
            WindowManagerImpl.getInstance().doFirePropertyChange(
                WindowManagerImpl.PROP_ACTIVE_MODE, oldActiveMode, mode);
        }
    }
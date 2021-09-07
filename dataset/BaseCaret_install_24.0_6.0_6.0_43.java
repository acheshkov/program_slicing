public @Override void install(JTextComponent c) {
        assert (SwingUtilities.isEventDispatchThread()); // must be done in AWT
        if (LOG.isLoggable(Level.FINE)) {
            LOG.fine("Installing to " + s2s(c)); //NOI18N
        }
        
        component = c;
        blinkVisible = true;
        
        // Assign dot and mark positions
        BaseDocument doc = Utilities.getDocument(c);
        if (doc != null) {
            modelChanged(null, doc);
        }

        // Attempt to assign initial bounds - usually here the component
        // is not yet added to the component hierarchy.
        updateCaretBounds();
        
        if (caretBounds == null) {
            // For null bounds wait for the component to get resized
            // and attempt to recompute bounds then
            component.addComponentListener(listenerImpl);
        }

        component.addPropertyChangeListener(this);
        component.addFocusListener(listenerImpl);
        component.addMouseListener(this);
        component.addMouseMotionListener(this);
        ViewHierarchy.get(component).addViewHierarchyListener(listenerImpl);

        EditorUI editorUI = Utilities.getEditorUI(component);
        editorUI.addPropertyChangeListener( this );
        
        if (component.hasFocus()) {
            if (LOG.isLoggable(Level.FINE)) {
                LOG.fine("Component has focus, calling BaseCaret.focusGained(); doc=" // NOI18N
                    + component.getDocument().getProperty(Document.TitleProperty) + '\n');
            }
            listenerImpl.focusGained(null); // emulate focus gained
        }

        dispatchUpdate(false);
    }
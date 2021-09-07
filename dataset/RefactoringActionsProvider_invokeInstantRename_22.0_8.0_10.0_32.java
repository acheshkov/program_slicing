private void invokeInstantRename(final Lookup lookup, final EditorCookie ec) {
        try {
            JEditorPane target = ec.getOpenedPanes()[0];
            final int caret = target.getCaretPosition();
            String ident = Utilities.getIdentifier(Utilities.getDocument(target), caret);
            
            if (ident == null) {
                Utilities.setStatusBoldText(target, WARN_CannotPerformHere());
                return;
            }
            
            DataObject od = (DataObject) target.getDocument().getProperty(Document.StreamDescriptionProperty);
            JavaSource js = od != null ? JavaSource.forFileObject(od.getPrimaryFile()) : null;

            if (js == null) {
                Utilities.setStatusBoldText(target, WARN_CannotPerformHere());
                return;
            }
            InstantRefactoringUI ui = InstantRefactoringUIImpl.create(js, caret);
            
            if (ui != null) {
                if (ui.getRegions().isEmpty() || ui.getKeyStroke() == null) {
                    doFullRename(lookup);
                } else {
                    doInstantRename(target, js, caret, ui);
                }
            } else {
                Utilities.setStatusBoldText(target, WARN_CannotPerformHere());
            }
        } catch (BadLocationException e) {
            Exceptions.printStackTrace(e);
        }
    }
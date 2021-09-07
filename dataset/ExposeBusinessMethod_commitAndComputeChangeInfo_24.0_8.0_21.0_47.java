private ChangeInfo commitAndComputeChangeInfo(final FileObject target, ModificationResult diff) throws IOException {
        List<? extends Difference> differences = diff.getDifferences(target);
        ChangeInfo result = null;

        // need to save the modified doc so that changes are recognized, see #112888
        CloneableEditorSupport docToSave = null;
        try {
            if (differences != null) {
                for (Difference d : differences) {
                    if (d.getNewText() != null) { //to filter out possible removes
                        final Position start = d.getStartPosition();
                        Document doc = d.openDocument();
                        if (docToSave == null) {
                            docToSave = target.getLookup().lookup(CloneableEditorSupport.class);
                        }
                        final Position[] pos = new Position[1];
                        final Document fdoc = doc;

                        doc.render(new Runnable() {
                            @Override
                            public void run() {
                                try {
                                    pos[0] = NbDocument.createPosition(fdoc, start.getOffset(), Position.Bias.Backward);
                                } catch (BadLocationException ex) {
                                    Exceptions.printStackTrace(ex);
                                }
                            }
                        });

                        if (pos[0] != null) {
                            result = new ChangeInfo(target, pos[0], pos[0]);
                        }
                        break;
                    }
                }
            }
        } catch (IOException e) {
            Exceptions.printStackTrace(e);
        }

        diff.commit();

        if (docToSave != null) {
            docToSave.saveDocument();
        }

        return result;
    }
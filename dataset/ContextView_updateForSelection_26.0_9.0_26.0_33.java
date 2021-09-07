private void updateForSelection() {
        Node[] nodes = explorerManager.getSelectedNodes();
        if (nodes.length == 0) {
            displayNoFileSelected();
        } else if (nodes.length == 1) {
            Node n = nodes[0];
            MatchingObject mo = n.getLookup().lookup(MatchingObject.class);
            if (mo != null) {
                displayFile(mo, -1);
            } else {
                Node parent = n.getParentNode();
                TextDetail td = n.getLookup().lookup(TextDetail.class);
                if (td != null && parent != null) {
                    mo = parent.getLookup().lookup(
                            MatchingObject.class);
                    if (mo != null) {
                        // TODO pass TextDetail directly
                        int index = -1;
                        for (int i = 0; i < mo.getTextDetails().size(); i++) {
                            if (mo.getTextDetails().get(i) == td) {
                                index = i;
                                break;
                            }
                        }
                        displayFile(mo, index);
                    }
                } else {
                    displayNoFileSelected();
                }
            }
        } else {
            displayMultipleItemsSelected();
        }
    }
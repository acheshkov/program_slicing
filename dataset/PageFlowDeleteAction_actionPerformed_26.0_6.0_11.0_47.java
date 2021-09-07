public void actionPerformed(ActionEvent event) {
        
        Queue<PageFlowSceneElement> deleteNodesList = new LinkedList<PageFlowSceneElement>();
        //Workaround: Temporarily Wrapping Collection because of Issue: 100127
        Set<Object> selectedObjects = new HashSet<Object>(scene.getSelectedObjects());
        LOG.fine("Selected Objects: " + selectedObjects);
        LOG.finest("Scene: \n" +
                "Nodes: " + scene.getNodes() + "\n" +
                "Edges: " + scene.getEdges()+ "\n" +
                "Pins: " + scene.getPins());
        
        /*When deleteing only one item. */
        if (selectedObjects.size() == 1){
            Object myObj = selectedObjects.toArray()[0];
            if( myObj instanceof PageFlowSceneElement ) {
                deleteNodesList.add((PageFlowSceneElement)myObj);
                deleteNodes(deleteNodesList);
                return;
            }
        }
        
        Set<NavigationCaseEdge> selectedEdges = new HashSet<NavigationCaseEdge>();
        Set<PageFlowSceneElement> selectedNonEdges = new HashSet<PageFlowSceneElement>();
        
        /* When deleting multiple objects, make sure delete all the links first. */
        Set<Object> nonEdgeSelectedObjects = new HashSet<Object>();
        for( Object selectedObj : selectedObjects ){
            if( selectedObj instanceof PageFlowSceneElement ){
                if( scene.isEdge(selectedObj) ){
                    assert !scene.isPin(selectedObj);
                    selectedEdges.add((NavigationCaseEdge)selectedObj);
                } else {
                    assert scene.isNode(selectedObj) || scene.isPin(selectedObj);
                    selectedNonEdges.add((PageFlowSceneElement)selectedObj);
                }
            }
        }
        
        /* I can not call deleteNodes on them separate because I need to guarentee that the edges are always deleted before anything else. */
        deleteNodesList.addAll(selectedEdges);
        deleteNodesList.addAll(selectedNonEdges);
        
        //        for( Object selectedObj : nonEdgeSelectedObjects ){
        //            deleteNodesList.add((PageFlowSceneElement)selectedObj);
        //        }
        deleteNodes(deleteNodesList);
        
    }
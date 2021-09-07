public final void layout(N rootNode) {
        if (rootNode == null) {
            return;
        }
        Collection<N> allNodes = scene.getNodes();
        ArrayList<N> nodesToResolve = new ArrayList<N> (allNodes);
        
        HashSet<N> loadedSet = new HashSet<N> ();
        Node root = new Node(rootNode, loadedSet);
        nodesToResolve.removeAll(loadedSet);
        if (vertical) {
            root.allocateHorizontally();
            root.resolveVertically(originX, originY);
        } else {
            root.allocateVertically();
            root.resolveHorizontally(originX, originY);
        }
        
        final HashMap<N, Point> resultPosition = new HashMap<N, Point> ();
        root.upload(resultPosition);
        
        for (N node : nodesToResolve) {
            Point position = new Point();
            // TODO - resolve others
            resultPosition.put(node, position);
        }
        
        for (Map.Entry<N, Point> entry : resultPosition.entrySet()) {
            scene.findWidget(entry.getKey()).setPreferredLocation(entry.getValue());
        }
        scene.validate();
    }
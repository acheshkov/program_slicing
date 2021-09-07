private void verticalSegmentToCNode(final VerticalSegment verticalSegment) {
        // create CNode representation for the last segment
        CNode cNode = CNode.of()
                           .origin(verticalSegment)
                           .type("vs")
                           .hitbox(new ElkRectangle(verticalSegment.hitbox))
                           .toStringDelegate(VS_TO_STRING_DELEGATE)
                           .create(cGraph);
        
        // group the node if requested, currently this is only the case for north/south segments of orthogonal edges 
        // assumption: during creation of LNode representing CNodes, these CNodes have been fitted with their own group
        if (!verticalSegment.potentialGroupParents.isEmpty()) {
            verticalSegment.potentialGroupParents.get(0).cGroup.addCNode(cNode);
        }
        
        Quadruplet vsLock = new Quadruplet();
        lockMap.put(cNode, vsLock);

        // segments belonging to multiple edges should be locked 
        // in the direction that fewer different ports are connected in
        // (only used if LEFT_RIGHT_CONNECTION_LOCKING is active)
        Set<LPort> inc = Sets.newHashSet();
        Set<LPort> out = Sets.newHashSet();
        for (LEdge e : verticalSegment.representedLEdges) {
            inc.add(e.getSource());
            out.add(e.getTarget());
        }
        int difference = inc.size() - out.size();
        if (difference < 0) {
            vsLock.set(true, Direction.LEFT);
            vsLock.set(false, Direction.RIGHT);
        } else if (difference > 0) {
            vsLock.set(false, Direction.LEFT);
            vsLock.set(true, Direction.RIGHT);
        }
        
        verticalSegment.joined.forEach(other -> verticalSegmentsMap.put(other, cNode));
        verticalSegmentsMap.put(verticalSegment, cNode);
    }
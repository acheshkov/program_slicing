private String generateElementUniqueID(LineNumberElement currentElement) {
        // extract parent info
        String parentGivenId = "";
        if (currentElement.getParentElement() == null) {
            parentGivenId = "root";
        } else {
            LineNumberElement elementParent = (LineNumberElement) currentElement.getParentElement();
            String rawId = elementParent.getName() + elementParent.getStartLine();
            parentGivenId = elementCache.get(rawId);
        }

        // generate self info
        String selfId = currentElement.getName();
        if (currentElement.getAttributes() != null && currentElement.getAttributes().size() > 0) {
            Attribute nameAttr = currentElement.getAttributes().get(0);
            if (!nameAttr.getName().equalsIgnoreCase("name")) {
                for (int i = 1; i < currentElement.getAttributes().size(); i++) {
                    Attribute attr = currentElement.getAttributes().get(i);
                    if (attr.getName().equalsIgnoreCase("name")) {
                        nameAttr = attr;
                        break;
                    }
                }
            }
            selfId = selfId + nameAttr.toString();
        } else {
            if (currentElement.getChildren().size() == 0 && currentElement.getContent().size() == 1) {
                selfId = selfId + "[" + currentElement.getText() + "]";
            } else {
                if (currentElement.getChildren().size() > 0) {
                    Element first = currentElement.getChildren().get(0);
                    if (isLeafNode(first)) {
                        Element second = null;
                        for (int i = 1; i < currentElement.getChildren().size(); i++) {
                            if (isLeafNode(currentElement.getChildren().get(i))) {
                                if (second == null) {
                                    second = currentElement.getChildren().get(i);
                                } else {
                                    break;
                                }
                            }
                        }
                        String text = first.getName() + "=" + first.getContent(0);
                        if (second != null) {
                            text = text + "," + second.getName() + "=" + second.getContent(0);
                        }
                        selfId = selfId + "[" + text + "]";
                        System.out.println(selfId);
                    }
                }
            }
        }

        if (parentChildCache.get(parentGivenId) == null) {
            parentChildCache.put(parentGivenId, new HashMap<String, HashSet<String>>());
        }

        if (parentChildCache.get(parentGivenId).get(selfId) == null) {
            parentChildCache.get(parentGivenId).put(selfId, new HashSet<String>());
        }

        if (parentChildCache.get(parentGivenId) != null && parentChildCache.get(parentGivenId).get(selfId) != null) {
            String selfGivenId = selfId + parentChildCache.get(parentGivenId).get(selfId).size();
            parentChildCache.get(parentGivenId).get(selfId).add(selfGivenId);
            selfId = selfGivenId;
        }

        String fullId = parentGivenId + "[" + selfId + "]";

        // save into the cache
        elementCache.put(currentElement.getName() + currentElement.getStartLine(), fullId);
        return fullId;
    }
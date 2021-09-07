private static void copyXMLTree(Document doc, Element from, Element to, String newNamespace) {
        NodeList nl = from.getChildNodes();
        int length = nl.getLength();
        for (int i = 0; i < length; i++) {
            org.w3c.dom.Node node = nl.item(i);
            org.w3c.dom.Node newNode;
            switch (node.getNodeType()) {
                case org.w3c.dom.Node.ELEMENT_NODE:
                    Element oldElement = (Element) node;
                    newNode = doc.createElementNS(newNamespace, oldElement.getTagName());
                    NamedNodeMap attrs = oldElement.getAttributes();
                    int alength = attrs.getLength();
                    for (int j = 0; j < alength; j++) {
                        org.w3c.dom.Attr oldAttr = (org.w3c.dom.Attr) attrs.item(j);
                        ((Element)newNode).setAttributeNS(oldAttr.getNamespaceURI(), oldAttr.getName(), oldAttr.getValue());
                    }
                    copyXMLTree(doc, oldElement, (Element) newNode, newNamespace);
                    break;
                case org.w3c.dom.Node.TEXT_NODE:
                    newNode = doc.createTextNode(((Text) node).getData());
                    break;
                case org.w3c.dom.Node.COMMENT_NODE:
                    newNode = doc.createComment(((Comment) node).getData());
                    break;
                default:
                    // Other types (e.g. CDATA) not yet handled.
                    throw new AssertionError(node);
            }
            to.appendChild(newNode);
        }
    }
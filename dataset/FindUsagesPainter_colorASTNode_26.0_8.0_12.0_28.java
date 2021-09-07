public static String colorASTNode(final ASTNode node, final Line line) {
        final int columnStart = node.getColumnNumber();
        final int columnEnd = node.getLastColumnNumber();

        if (node instanceof ClassNode) {
            return colorLine(line, ((ClassNode) node).getNameWithoutPackage());
        } else if (node instanceof ConstructorNode) {
            return colorLine(line, ((ConstructorNode) node).getDeclaringClass().getNameWithoutPackage());
        } else if (node instanceof ConstructorCallExpression) {
            return colorLine(line, ((ConstructorCallExpression) node).getType().getNameWithoutPackage());
        } else if (node instanceof MethodNode) {
            return colorLine(line, ((MethodNode) node).getName());
        } else if (node instanceof FieldNode) {
            return colorLine(line, ((FieldNode) node).getName());
        } else if (node instanceof FakeASTNode) {
            // I know this isn't the nicest way, but I can't pass ImportNode directly and
            // don't see easier way how to find out if the FakeASTNode is based on ImportNode
            ASTNode originalNode = ((FakeASTNode) node).getOriginalNode();
            if (originalNode instanceof ImportNode) {
                return colorLine(line, ((ImportNode) originalNode).getAlias());
            }
        }

        final String beforePart = line.createPart(0, columnStart - 1).getText();
        final String usagePart = line.createPart(columnStart - 1, columnEnd - columnStart).getText();
        final String afterPart = line.createPart(columnEnd - 1, line.getText().length()).getText();

        return buildHTML(beforePart, usagePart, afterPart);
    }
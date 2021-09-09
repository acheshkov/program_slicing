@NonNull
    public static OffsetRange getRange(ASTNode node, BaseDocument doc) {

        // Warning! The implicit class and some other nodes has line/column numbers below 1
        // if line is wrong, let's invalidate also column and vice versa
        int lineNumber = node.getLineNumber();
        int columnNumber = node.getColumnNumber();
        if (lineNumber < 1 || columnNumber < 1) {
            return OffsetRange.NONE;
        }
        if (doc == null) {
            LOGGER.log(Level.INFO, "Null document in getRange()");
            return OffsetRange.NONE;
        }

        if (node instanceof FieldNode) {
            int start = getOffset(doc, lineNumber, columnNumber);
            FieldNode fieldNode = (FieldNode) node;
            return getNextIdentifierByName(doc, fieldNode.getName(), start);
        } else if (node instanceof ClassNode) {
            final ClassNode classNode = (ClassNode) node;
            int start = getOffset(doc, lineNumber, columnNumber);

            // classnode for script does not have real declaration and thus location
            if (classNode.isScript()) {
                return getNextIdentifierByName(doc, classNode.getNameWithoutPackage(), start);
            }

            // ok, here we have to move the Range to the first character
            // after the "class" keyword, plus an indefinite nuber of spaces
            // FIXME: have to check what happens with other whitespaces between
            // the keyword and the identifier (like newline)

            // happens in some cases when groovy source uses some non-imported java class
            if (doc != null) {

                // if we are dealing with an empty groovy-file, we have take into consideration,
                // that even though we're running on an ClassNode, there is no "class " String
                // in the sourcefile. So take doc.getLength() as maximum.

                int docLength = doc.getLength();
                int limit = getLimit(node, doc, docLength);

                try {
                    // we have to really search for class keyword other keyword
                    // (such as abstract) can precede class
                    start = doc.find(new FinderFactory.StringFwdFinder("class", true), start, limit) + "class".length(); // NOI18N
                } catch (BadLocationException ex) {
                    LOGGER.log(Level.WARNING, null, ex);
                }

                if (start > docLength) {
                    start = docLength;
                }

                try {
                    start = Utilities.getFirstNonWhiteFwd(doc, start);
                } catch (BadLocationException ex) {
                    Exceptions.printStackTrace(ex);
                }

                // This seems to happen every now and then ...
                if (start < 0) {
                    start = 0;
                }

                int end = start + classNode.getNameWithoutPackage().length();

                if (end > docLength) {
                    end = docLength;
                }

                if (start == end) {
                    return OffsetRange.NONE;
                }
                return new OffsetRange(start, end);
            }
        } else if (node instanceof ConstructorNode) {
            int start = getOffset(doc, lineNumber, columnNumber);
            ConstructorNode constructorNode = (ConstructorNode) node;
            return getNextIdentifierByName(doc, constructorNode.getDeclaringClass().getNameWithoutPackage(), start);
        } else if (node instanceof MethodNode) {
            int start = getOffset(doc, lineNumber, columnNumber);
            MethodNode methodNode = (MethodNode) node;
            return getNextIdentifierByName(doc, methodNode.getName(), start);
        } else if (node instanceof VariableExpression) {
            int start = getOffset(doc, lineNumber, columnNumber);
            VariableExpression variableExpression = (VariableExpression) node;
            return getNextIdentifierByName(doc, variableExpression.getName(), start);
        } else if (node instanceof Parameter) {

            int docLength = doc.getLength();
            int start = getOffset(doc, node.getLineNumber(), node.getColumnNumber());
            int limit = getLimit(node, doc, docLength);

            Parameter parameter = (Parameter) node;
            String name = parameter.getName();

            try {
                // we have to really search for the name
                start = doc.find(new FinderFactory.StringFwdFinder(name, true), start, limit);
            } catch (BadLocationException ex) {
                Exceptions.printStackTrace(ex);
            }

            int end = start + name.length();
            if (end > docLength) {
                return OffsetRange.NONE;
            }
            return getNextIdentifierByName(doc, name, start);
        } else if (node instanceof MethodCallExpression) {
            MethodCallExpression methodCall = (MethodCallExpression) node;
            Expression method = methodCall.getMethod();
            lineNumber = method.getLineNumber();
            columnNumber = method.getColumnNumber();
            if (lineNumber < 1 || columnNumber < 1) {
                lineNumber = 1;
                columnNumber = 1;
            }
            int start = getOffset(doc, lineNumber, columnNumber);
            return new OffsetRange(start, start + methodCall.getMethodAsString().length());
        } else if (node instanceof ConstructorCallExpression) {
            ConstructorCallExpression methodCall = (ConstructorCallExpression) node;
            String name = methodCall.getType().getNameWithoutPackage();
            // +4 because we don't want to have "new " in the offset
            // would be good to do this in more sofisticated way than this shit
            int start = getOffset(doc, lineNumber, columnNumber + 4);
            return getNextIdentifierByName(doc, name, start);
        } else if (node instanceof ClassExpression) {
            ClassExpression clazz = (ClassExpression) node;
            String name = clazz.getType().getNameWithoutPackage();
            int start = getOffset(doc, lineNumber, columnNumber);
            return getNextIdentifierByName(doc, name, start);
        } else if (node instanceof ConstantExpression) {
            ConstantExpression constantExpression = (ConstantExpression) node;
            int start = getOffset(doc, lineNumber, columnNumber);
            return new OffsetRange(start, start + constantExpression.getText().length());
        } else if (node instanceof FakeASTNode) {
            final String typeName = ElementUtils.getTypeNameWithoutPackage(((FakeASTNode) node).getOriginalNode());
            final int start = getOffset(doc, lineNumber, columnNumber);
            
            return getNextIdentifierByName(doc, typeName, start);
        }
        return OffsetRange.NONE;
    }
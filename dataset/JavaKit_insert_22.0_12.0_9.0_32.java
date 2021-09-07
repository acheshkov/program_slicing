@Override
        public void insert(MutableContext context) throws BadLocationException {
            int dotPos = context.getCaretOffset();
            Document doc = context.getDocument();
            if(TypingCompletion.posWithinTextBlock(doc, dotPos))return;
            if (TypingCompletion.posWithinString(doc, dotPos)) {
                if (CodeStyle.getDefault(doc).wrapAfterBinaryOps()) {
                    context.setText("\" +\n \"", 3, 6); // NOI18N
                } else {
                    context.setText("\"\n + \"", 1, 6); // NOI18N
                }
                return;
            } 
            
            BaseDocument baseDoc = (BaseDocument) context.getDocument();
            if (TypingCompletion.isCompletionSettingEnabled() && TypingCompletion.isAddRightBrace(baseDoc, dotPos)) {
                boolean insert[] = {true};
                int end = TypingCompletion.getRowOrBlockEnd(baseDoc, dotPos, insert);
                if (insert[0]) {
                    doc.insertString(end, "}", null); // NOI18N
                    Indent.get(doc).indentNewLine(end);
                }
                context.getComponent().getCaret().setDot(dotPos);
            } else {
                if (TypingCompletion.blockCommentCompletion(context)) {
                    blockCommentComplete(doc, dotPos, context);
                }
                isJavadocTouched = TypingCompletion.javadocBlockCompletion(context);
                if (isJavadocTouched) {
                    blockCommentComplete(doc, dotPos, context);
                }
            }
        }
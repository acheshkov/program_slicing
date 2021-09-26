private boolean sanitizeSource(Context context, Sanitize sanitizing, JsErrorManager errorManager) {
        if (sanitizing == Sanitize.MISSING_CURLY) {
            org.netbeans.modules.csl.api.Error error = errorManager.getMissingCurlyError();
            if (error != null) {
                int offset = error.getStartPosition();
                return sanitizeBrackets(sanitizing, context, offset, '{', '}'); // NOI18N
            }
        } else if (sanitizing == Sanitize.MISSING_SEMICOLON) {
            org.netbeans.modules.csl.api.Error error = errorManager.getMissingSemicolonError();
            if (error != null) {
                String source = context.getOriginalSource();

                boolean ok = false;
                StringBuilder builder = new StringBuilder(source);
                if (error.getStartPosition() >= source.length()) {
                    builder.append(';'); // NOI18N
                    ok = true;
                } else {
                    int replaceOffset = error.getStartPosition();
                    if (replaceOffset >= 0 && Character.isWhitespace(replaceOffset)) {
                        builder.delete(replaceOffset, replaceOffset + 1);
                        builder.insert(replaceOffset, ';'); // NOI18N
                        ok = true;
                    }
                }

                if (ok) {
                    context.setSanitizedSource(builder.toString());
                    context.setSanitization(sanitizing);
                    return true;
                }
            }
        } else if (sanitizing == Sanitize.SYNTAX_ERROR_CURRENT) {
            List<? extends org.netbeans.modules.csl.api.Error> errors = errorManager.getErrors();
            if (!errors.isEmpty()) {
                org.netbeans.modules.csl.api.Error error = errors.get(0);
                int offset = error.getStartPosition();
                TokenSequence<? extends JsTokenId> ts = LexUtilities.getTokenSequence(
                        context.getSnapshot(), 0, language);
                if (ts != null) {
                    ts.move(offset);
                    if (ts.moveNext()) {
                        int start = ts.offset();
                        if (start >= 0 && ts.moveNext()) {
                            int end = ts.offset();
                            ts.movePrevious();
                            while(ts.movePrevious() && ts.token().id() == JsTokenId.WHITESPACE) {
                            }
                            if (ts.token().id() == JsTokenId.OPERATOR_DOT) {
                                start = ts.offset();
                            }
                            StringBuilder builder = new StringBuilder(context.getOriginalSource());
                            erase(builder, start, end);
                            context.setSanitizedSource(builder.toString());
                            context.setSanitization(sanitizing);
                            return true;
                        }
                    }
                }
            }
        } else if (sanitizing == Sanitize.SYNTAX_ERROR_PREVIOUS) {
            List<? extends org.netbeans.modules.csl.api.Error> errors = errorManager.getErrors();
            if (!errors.isEmpty()) {
                org.netbeans.modules.csl.api.Error error = errors.get(0);
                int offset = error.getStartPosition();
                return sanitizePrevious(sanitizing, context, offset, new TokenCondition() {

                    @Override
                    public boolean found(JsTokenId id) {
                        return id != JsTokenId.WHITESPACE
                                && id != JsTokenId.EOL
                                && id != JsTokenId.DOC_COMMENT
                                && id != JsTokenId.LINE_COMMENT
                                && id != JsTokenId.BLOCK_COMMENT;
                    }
                });
            }
        } else if (sanitizing == Sanitize.MISSING_PAREN) {
            List<? extends org.netbeans.modules.csl.api.Error> errors = errorManager.getErrors();
            if (!errors.isEmpty()) {
                org.netbeans.modules.csl.api.Error error = errors.get(0);
                int offset = error.getStartPosition();
                return sanitizeBrackets(sanitizing, context, offset, '(', ')'); // NOI18N
            }
        } else if (sanitizing == Sanitize.ERROR_DOT) {
            List<? extends org.netbeans.modules.csl.api.Error> errors = errorManager.getErrors();
            if (!errors.isEmpty()) {
                org.netbeans.modules.csl.api.Error error = errors.get(0);
                int offset = error.getStartPosition();
                return sanitizePrevious(sanitizing, context, offset, new TokenCondition() {

                    @Override
                    public boolean found(JsTokenId id) {
                        return id == JsTokenId.OPERATOR_DOT;
                    }
                });
            }
        } else if (sanitizing == Sanitize.ERROR_LINE) {
            List<? extends org.netbeans.modules.csl.api.Error> errors = errorManager.getErrors();
            if (!errors.isEmpty()) {
                org.netbeans.modules.csl.api.Error error = errors.get(0);
                int offset = error.getStartPosition();
                return sanitizeLine(sanitizing, context, offset);
            }
        } else if (sanitizing == Sanitize.EDITED_LINE) {
            int offset = context.getCaretOffset();
            return sanitizeLine(sanitizing, context, offset);
        } else if (sanitizing == Sanitize.PREVIOUS_LINES) {
            StringBuilder result = new StringBuilder(context.getOriginalSource());
            for (org.netbeans.modules.csl.api.Error error : errorManager.getErrors()) {
                TokenSequence<? extends JsTokenId> ts = LexUtilities.getTokenSequence(
                        context.getSnapshot(), error.getStartPosition(), language);
                if (ts != null) {
                    ts.move(error.getStartPosition());
                    if (ts.movePrevious()) {
                        LexUtilities.findPreviousIncluding(ts, Collections.singletonList(JsTokenId.EOL));
                        if (!sanitizeLine(context.getOriginalSource(), result, ts.offset())) {
                            return false;
                        }
                    } else {
                        return false;
                    }
                } else {
                    return false;
                }
            }
            context.setSanitizedSource(result.toString());
            context.setSanitization(sanitizing);
            return true;
        }
        return false;
    }
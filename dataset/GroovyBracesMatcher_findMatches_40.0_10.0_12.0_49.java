public int [] findMatches() throws InterruptedException, BadLocationException {
        ((AbstractDocument) context.getDocument()).readLock();
        try {
            BaseDocument doc = (BaseDocument) context.getDocument();
            
            int offset = context.getSearchOffset();

            TokenSequence<GroovyTokenId> ts = LexUtilities.getGroovyTokenSequence(doc, offset);

            if (ts != null) {
                ts.move(offset);

                if (!ts.moveNext()) {
                    return null;
                }

                Token<GroovyTokenId> token = ts.token();

                if (token == null) {
                    return null;
                }
                
                TokenId id = token.id();
                
                OffsetRange r;
                if (id == GroovyTokenId.LPAREN) {
                    r = LexUtilities.findFwd(doc, ts, GroovyTokenId.LPAREN, GroovyTokenId.RPAREN);
                    return new int [] {r.getStart(), r.getEnd() };
                } else if (id == GroovyTokenId.RPAREN) {
                    r = LexUtilities.findBwd(doc, ts, GroovyTokenId.LPAREN, GroovyTokenId.RPAREN);
                    return new int [] {r.getStart(), r.getEnd() };
                } else if (id == GroovyTokenId.LBRACE) {
                    r = LexUtilities.findFwd(doc, ts, GroovyTokenId.LBRACE, GroovyTokenId.RBRACE);
                    return new int [] {r.getStart(), r.getEnd() };
                } else if (id == GroovyTokenId.RBRACE) {
                    r = LexUtilities.findBwd(doc, ts, GroovyTokenId.LBRACE, GroovyTokenId.RBRACE);
                    return new int [] {r.getStart(), r.getEnd() };
                } else if (id == GroovyTokenId.LBRACKET) {
                    r = LexUtilities.findFwd(doc, ts, GroovyTokenId.LBRACKET, GroovyTokenId.RBRACKET);
                    return new int [] {r.getStart(), r.getEnd() };
                } else if (id == GroovyTokenId.RBRACKET) {
                    r = LexUtilities.findBwd(doc, ts, GroovyTokenId.LBRACKET, GroovyTokenId.RBRACKET);
                    return new int [] {r.getStart(), r.getEnd() };
                }
            }
            return null;
        } finally {
            ((AbstractDocument) context.getDocument()).readUnlock();
        }
    }
private void handlePhpdocTag(CharSequence tag) {
        if ("@see".contentEquals(tag)) { // NOI18N
            // e.g.
            // @see MyClass::$items
            // @see http://example.com/my/bar Documentation of Foo.
            // ignore next "word"
            Pair<CharSequence, Integer> data = wordBroker(currentBlockText, currentOffsetInComment, LetterType.See);
            currentOffsetInComment = getCurrentOffsetInComment(data);
            return;
        }

        if ("@author".contentEquals(tag)) { // NOI18N
            // ignore everything till the end of the line:
            Pair<CharSequence, Integer> data = wordBroker(currentBlockText, currentOffsetInComment);
            while (data != null) {
                currentOffsetInComment = getCurrentOffsetInComment(data);
                if ('\n' == data.first().charAt(0)) {
                    // continue
                    return;
                }
                data = wordBroker(currentBlockText, currentOffsetInComment);
            }
            return;
        }

        if (currentDocBlock != null) {
            List<PHPDocTag> phpDocTags = currentDocBlock.getTags();
            for (PHPDocTag phpDocTag : phpDocTags) {
                if (phpDocTag.getStartOffset() == currentOffsetInComment - tag.length()) {
                    if (phpDocTag instanceof PHPDocTypeTag) {
                        handleTypeTag((PHPDocTypeTag) phpDocTag);
                    }
                    break;
                }
            }
        }
    }
private void parseSub(XContentParser parser, FieldParser fieldParser, String currentFieldName, Value value, Context context)
            throws IOException {
        final XContentParser.Token token = parser.currentToken();
        switch (token) {
            case START_OBJECT:
                parseValue(parser, fieldParser, currentFieldName, value, context);
                /*
                 * Well behaving parsers should consume the entire object but
                 * asserting that they do that is not something we can do
                 * efficiently here. Instead we can check that they end on an
                 * END_OBJECT. They could end on the *wrong* end object and
                 * this test won't catch them, but that is the price that we pay
                 * for having a cheap test.
                 */
                if (parser.currentToken() != XContentParser.Token.END_OBJECT) {
                    throw new IllegalStateException("parser for [" + currentFieldName + "] did not end on END_OBJECT");
                }
                break;
            case START_ARRAY:
                parseArray(parser, fieldParser, currentFieldName, value, context);
                /*
                 * Well behaving parsers should consume the entire array but
                 * asserting that they do that is not something we can do
                 * efficiently here. Instead we can check that they end on an
                 * END_ARRAY. They could end on the *wrong* end array and
                 * this test won't catch them, but that is the price that we pay
                 * for having a cheap test.
                 */
                if (parser.currentToken() != XContentParser.Token.END_ARRAY) {
                    throw new IllegalStateException("parser for [" + currentFieldName + "] did not end on END_ARRAY");
                }
                break;
            case END_OBJECT:
            case END_ARRAY:
            case FIELD_NAME:
                throw new XContentParseException(parser.getTokenLocation(), "[" + name + "]" + token + " is unexpected");
            case VALUE_STRING:
            case VALUE_NUMBER:
            case VALUE_BOOLEAN:
            case VALUE_EMBEDDED_OBJECT:
            case VALUE_NULL:
                parseValue(parser, fieldParser, currentFieldName, value, context);
        }
    }
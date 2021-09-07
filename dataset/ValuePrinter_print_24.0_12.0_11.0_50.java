public static String print(final Object value) {
        if (value == null) {
            return "null";
        }
        if (value instanceof String) {
            return '"' + value.toString() + '"';
        }
        if (value instanceof Character) {
            return printChar((Character) value);
        }
        if (value instanceof Long) {
            return value + "L";
        }
        if (value instanceof Double) {
            return value + "d";
        }
        if (value instanceof Float) {
            return value + "f";
        }
        if (value instanceof Short) {
            return "(short) " + value;
        }
        if (value instanceof Byte) {
            return String.format("(byte) 0x%02X", (Byte) value);
        }
        if (value instanceof Map) {
            return printMap((Map<?, ?>) value);
        }
        if (value.getClass().isArray()) {
            return printValues("[", ", ", "]", new Iterator<Object>() {
                private int currentIndex = 0;

                public boolean hasNext() {
                    return currentIndex < Array.getLength(value);
                }

                public Object next() {
                    return Array.get(value, currentIndex++);
                }

                public void remove() {
                    throw new UnsupportedOperationException("cannot remove items from an array");
                }
            });
        }
        if (value instanceof FormattedText) {
            return (((FormattedText) value).getText());
        }

        return descriptionOf(value);
    }
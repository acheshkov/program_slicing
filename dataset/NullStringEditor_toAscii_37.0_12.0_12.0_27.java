private static String toAscii (String str) {
        StringBuffer buf = new StringBuffer (str.length() * 6); // x -> \u1234
        char[] chars = str.toCharArray();
        for (int i = 0; i < chars.length; i++) {
            char c = chars[i];
            switch (c) {
            case '\b': buf.append ("\\b"); break; // NOI18N
            case '\t': buf.append ("\\t"); break; // NOI18N
            case '\n': buf.append ("\\n"); break; // NOI18N
            case '\f': buf.append ("\\f"); break; // NOI18N
            case '\r': buf.append ("\\r"); break; // NOI18N
            case '\"': buf.append ("\\\""); break; // NOI18N
//  	    case '\'': buf.append ("\\'"); break; // NOI18N
            case '\\': buf.append ("\\\\"); break; // NOI18N
            default:
                if (c >= 0x0020 && c <= 0x007f)
                    buf.append (c);
                else {
                    buf.append ("\\u"); // NOI18N
                    String hex = Integer.toHexString (c);
                    for (int j = 0; j < 4 - hex.length(); j++)
                        buf.append ('0');
                    buf.append (hex);
                }
            }
        }
        return buf.toString();
    }
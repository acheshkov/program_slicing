boolean variable(Context context, DeclarationList declList) throws ParserException {
        int backIndex = tokens.index;
        String spacing = tokens.get().spacing;
        String modifiers = "public static native ";
        String setterType = "void ";
        Declarator dcl = declarator(context, null, 0, false, 0, false, true);
        Declaration decl = new Declaration();
        String cppName = dcl.cppName;
        String javaName = dcl.javaName;
        if (javaName == null || !tokens.get().match('[', '=', ',', ':', ';')) {
            tokens.index = backIndex;
            return false;
        } else if (!dcl.type.staticMember && context.javaName != null) {
            modifiers = "public native ";
            setterType = context.shorten(context.javaName) + " ";
        }

        int namespace = cppName.lastIndexOf("::");
        if (context.namespace != null && namespace < 0) {
            cppName = context.namespace + "::" + cppName;
        }
        Info info = infoMap.getFirst(cppName);
        if (info != null && info.skip) {
            decl.text = spacing;
            declList.add(decl);
            return true;
        } else if (info == null) {
            Info info2 = infoMap.getFirst(dcl.cppName);
            infoMap.put(info2 != null ? new Info(info2).cppNames(cppName) : new Info(cppName));
        }
        boolean first = true;
        Declarator metadcl = context.variable;
        for (int n = 0; n < Integer.MAX_VALUE; n++) {
            decl = new Declaration();
            tokens.index = backIndex;
            dcl = declarator(context, null, -1, false, n, false, true);
            if (dcl == null) {
                break;
            }
            decl.declarator = dcl;
            cppName = dcl.cppName;
            namespace = cppName.lastIndexOf("::");
            if (context.namespace != null && namespace < 0) {
                cppName = context.namespace + "::" + cppName;
            }
            info = infoMap.getFirst(cppName);

            namespace = cppName.lastIndexOf("::");
            String shortName = cppName;
            if (namespace >= 0) {
                shortName = cppName.substring(namespace + 2);
            }
            javaName = dcl.javaName;
            if (metadcl == null || metadcl.indices == 0 || dcl.indices == 0) {
                // arrays are currently not supported for both metadcl and dcl at the same time
                String indices = "";
                for (int i = 0; i < (metadcl == null || metadcl.indices == 0 ? dcl.indices : metadcl.indices); i++) {
                    if (i > 0) {
                        indices += ", ";
                    }
                    indices += "int " + (char)('i' + i);
                }
                if (context.namespace != null && context.javaName == null) {
                    decl.text += "@Namespace(\"" + context.namespace + "\") ";
                }
                if (metadcl != null && metadcl.cppName.length() > 0) {
                    decl.text += metadcl.indices == 0
                            ? "@Name(\"" + metadcl.cppName + "." + shortName + "\") "
                            : "@Name({\"" + metadcl.cppName + "\", \"." + shortName + "\"}) ";
                    javaName = metadcl.javaName + "_" + dcl.javaName;
                }
                if (dcl.type.constValue) {
                    decl.text += "@MemberGetter ";
                }
                decl.text += modifiers + dcl.type.annotations.replace("@ByVal ", "@ByRef ")
                          + dcl.type.javaName + " " + javaName + "(" + indices + ");";
                if (!dcl.type.constValue) {
                    if (indices.length() > 0) {
                        indices += ", ";
                    }
                    decl.text += " " + modifiers + setterType + javaName + "(" + indices + dcl.type.javaName + " " + javaName + ");";
                }
                decl.text += "\n";
                if (dcl.type.constValue && dcl.type.staticMember && indices.length() == 0) {
                    String rawType = dcl.type.javaName.substring(dcl.type.javaName.lastIndexOf(' ') + 1);
                    if ("byte".equals(rawType) || "short".equals(rawType) || "int".equals(rawType) || "long".equals(rawType)
                            || "float".equals(rawType) || "double".equals(rawType) || "char".equals(rawType) || "boolean".equals(rawType)) {
                        // only mind of what looks like constants that we can keep without hogging memory
                        decl.text += "public static final " + rawType + " " + javaName + " = " + javaName + "();\n";
                    }
                }
            }
            if (dcl.indices > 0) {
                // in the case of arrays, also add a pointer accessor
                tokens.index = backIndex;
                dcl = declarator(context, null, -1, false, n, true, false);
                String indices = "";
                for (int i = 0; i < (metadcl == null ? 0 : metadcl.indices); i++) {
                    if (i > 0) {
                        indices += ", ";
                    }
                    indices += "int " + (char)('i' + i);
                }
                if (context.namespace != null && context.javaName == null) {
                    decl.text += "@Namespace(\"" + context.namespace + "\") ";
                }
                if (metadcl != null && metadcl.cppName.length() > 0) {
                    decl.text += metadcl.indices == 0
                            ? "@Name(\"" + metadcl.cppName + "." + shortName + "\") "
                            : "@Name({\"" + metadcl.cppName + "\", \"." + shortName + "\"}) ";
                    javaName = metadcl.javaName + "_" + dcl.javaName;
                }
                decl.text += "@MemberGetter " + modifiers + dcl.type.annotations.replace("@ByVal ", "@ByRef ")
                          + dcl.type.javaName + " " + javaName + "(" + indices + ");\n";
            }
            decl.signature = dcl.signature;
            if (info != null && info.javaText != null) {
                decl.text = info.javaText;
                decl.declarator = null;
            }
            while (!tokens.get().match(Token.EOF, ';')) {
                tokens.next();
            }
            tokens.next();
            String comment = commentAfter();
            if (first) {
                first = false;
                declList.spacing = spacing;
                decl.text = comment + decl.text;
            }
            decl.variable = true;
            declList.add(decl);
        }
        declList.spacing = null;
        return true;
    }
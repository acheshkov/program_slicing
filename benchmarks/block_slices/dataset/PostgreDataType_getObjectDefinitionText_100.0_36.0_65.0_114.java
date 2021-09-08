@Override
    public String getObjectDefinitionText(DBRProgressMonitor monitor, Map<String, Object> options) throws DBException {
        StringBuilder sql = new StringBuilder();

        if (typeType == PostgreTypeType.d) {
            sql.append("-- DROP DOMAIN ").append(getFullyQualifiedName(DBPEvaluationContext.DDL)).append(";\n\n");
        } else {
            sql.append("-- DROP TYPE ").append(getFullyQualifiedName(DBPEvaluationContext.DDL)).append(";\n\n");
        }

        switch (typeType) {
            case p: {
                sql.append("CREATE TYPE ").append(getFullyQualifiedName(DBPEvaluationContext.DDL)).append(";");
                break;
            }
            case d: {
                sql.append("CREATE DOMAIN ").append(getFullyQualifiedName(DBPEvaluationContext.DDL)).append(" AS ").append(getBaseType(monitor).getFullyQualifiedName(DBPEvaluationContext.DDL));
                PostgreCollation collation = getCollationId(monitor);
                if (collation != null) {
                    sql.append("\n\tCOLLATE ").append(collation.getName());
                }
                if (!CommonUtils.isEmpty(defaultValue)) {
                    sql.append("\n\tDEFAULT ").append(defaultValue);
                }
                String constraint = getConstraint(monitor);
                if (!CommonUtils.isEmpty(constraint)) {
                    sql.append("\n\tCONSTRAINT ").append(constraint);
                }

                sql.append(";");
                break;
            }
            case e: {
                sql.append("CREATE TYPE ").append(getFullyQualifiedName(DBPEvaluationContext.DDL)).append(" AS ENUM (\n");
                if (enumValues != null) {
                    for (int i = 0; i < enumValues.length; i++) {
                        Object item = enumValues[i];
                        sql.append("\t").append(SQLUtils.quoteString(this, CommonUtils.toString(item)));
                        if (i < enumValues.length - 1) sql.append(",\n");
                    }
                }
                sql.append(");\n");
                break;
            }
            case r: {
                sql.append("CREATE TYPE ").append(getFullyQualifiedName(DBPEvaluationContext.DDL)).append(" AS RANGE (\n");
                PostgreCollation collation = getCollationId(monitor);
                appendCreateTypeParameter(sql, "COLLATION ", collation.getName());
                appendCreateTypeParameter(sql, "CANONICAL", canonicalName);
                // TODO: read data from pg_range
//                if (!CommonUtils.isEmpty(su)) {
//                    sql.append("\n\tCOLLATION ").append(canonicalName);
//                }
                sql.append(");\n");
                break;
            }
            case b: {
                sql.append("CREATE TYPE ").append(getFullyQualifiedName(DBPEvaluationContext.DDL)).append(" (");

                if (isValidFuncRef(inputFunc)) appendCreateTypeParameter(sql, "INPUT", inputFunc);
                if (isValidFuncRef(outputFunc)) appendCreateTypeParameter(sql, "OUTPUT", outputFunc);
                if (isValidFuncRef(receiveFunc)) appendCreateTypeParameter(sql, "RECEIVE", receiveFunc);
                if (isValidFuncRef(sendFunc)) appendCreateTypeParameter(sql, "SEND", sendFunc);
                if (isValidFuncRef(modInFunc)) appendCreateTypeParameter(sql, "TYPMOD_IN", modInFunc);
                if (isValidFuncRef(modOutFunc)) appendCreateTypeParameter(sql, "TYPMOD_OUT", modOutFunc);
                if (isValidFuncRef(analyzeFunc)) appendCreateTypeParameter(sql, "ANALYZE", analyzeFunc);
                if (getMaxLength() > 0) appendCreateTypeParameter(sql, "INTERNALLENGTH", getMaxLength());
                if (isByValue) appendCreateTypeParameter(sql, "PASSEDBYVALUE");
                if (align != null && align.getBytes() > 1) appendCreateTypeParameter(sql, "ALIGNMENT", align.getBytes());
                if (storage != null) appendCreateTypeParameter(sql, "STORAGE", storage.getName());
                if (typeCategory != null) appendCreateTypeParameter(sql, "CATEGORY", typeCategory.name());
                if (isPreferred) appendCreateTypeParameter(sql, "PREFERRED", isPreferred);
                appendCreateTypeParameter(sql, "DEFAULT", defaultValue);

                PostgreDataType elementType = getElementType(monitor);
                if (elementType != null) {
                    appendCreateTypeParameter(sql, "ELEMENT", elementType.getFullyQualifiedName(DBPEvaluationContext.DDL));
                }
                if (!CommonUtils.isEmpty(arrayDelimiter)) appendCreateTypeParameter(sql, "DELIMITER", SQLUtils.quoteString(getDataSource(), arrayDelimiter));
                if (collationId != 0) appendCreateTypeParameter(sql, "COLLATABLE", true);

                sql.append(");\n");
                break;
            }
            case c: {
                sql.append("CREATE TYPE ").append(getFullyQualifiedName(DBPEvaluationContext.DDL)).append(" AS (");
                Collection<PostgreDataTypeAttribute> attributes = getAttributes(monitor);
                if (!CommonUtils.isEmpty(attributes)) {
                    boolean first = true;
                    for (PostgreDataTypeAttribute attr : attributes) {
                        if (!first) sql.append(",");
                        first = false;

                        sql.append("\n\t")
                            .append(DBUtils.getQuotedIdentifier(attr)).append(" ").append(attr.getTypeName());
                        String modifiers = SQLUtils.getColumnTypeModifiers(getDataSource(), attr, attr.getTypeName(), attr.getDataKind());
                        if (modifiers != null) sql.append(modifiers);
                    }
                }
                sql.append(");\n");
                break;
            }
            default: {
                sql.append("-- Data type ").append(getFullyQualifiedName(DBPEvaluationContext.UI)).append(" (").append(typeType.getName()).append(") DDL is not supported\n");
                break;
            }
        }

        String description = getDescription();
        if (!CommonUtils.isEmpty(description)) {
            sql.append("\nCOMMENT ON TYPE ").append(getFullyQualifiedName(DBPEvaluationContext.DDL)).append(" IS ").append(SQLUtils.quoteString(this, description));
        }

        return sql.toString();
    }
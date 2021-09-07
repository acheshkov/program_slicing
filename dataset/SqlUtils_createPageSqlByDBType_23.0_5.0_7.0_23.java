public static String createPageSqlByDBType(String dbType, String sql, int page, int rows) {
        int beginNum = (page - 1) * rows;
        Object[] sqlParam = new Object[3];
        sqlParam[0] = sql;
        sqlParam[1] = String.valueOf(beginNum);
        sqlParam[2] = String.valueOf(rows);
        if (dbTypeIsMySQL(dbType)) {
            sql = MessageFormat.format(MYSQL_SQL, sqlParam);
        } else if (dbTypeIsPostgre(dbType)) {
            sql = MessageFormat.format(POSTGRE_SQL, sqlParam);
        } else {
            int beginIndex = (page - 1) * rows;
            int endIndex = beginIndex + rows;
            sqlParam[2] = Integer.toString(beginIndex);
            sqlParam[1] = Integer.toString(endIndex);
            if (dbTypeIsOracle(dbType)) {
                sql = MessageFormat.format(ORACLE_SQL, sqlParam);
            } else if (dbTypeIsSQLServer(dbType)) {
                sqlParam[0] = sql.substring(getAfterSelectInsertPoint(sql));
                sql = MessageFormat.format(SQLSERVER_SQL, sqlParam);
            }
        }
        return sql;
    }
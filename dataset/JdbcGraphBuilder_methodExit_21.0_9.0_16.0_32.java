@Override
    public void methodExit(int methodId, int threadId, int methodType, long timeStamp0, long timeStamp1, Object retVal) {
        if (methodType == METHODTYPE_MARKER) {
            if (status == null || (threadInfos.threadInfos == null)) {
                return;
            }

            ThreadInfo ti = threadInfos.threadInfos[threadId];

            if (ti == null) {
                return;
            }
            int sqlCallLevel = decrementSqlLevel(ti);

            plainMethodExit(methodId, ti, timeStamp0, timeStamp1, true);
            if (sqlCallLevel == 0) {
                SQLStatement st = currentObject.get(ti);
                
                if (st != null && retVal instanceof String) {
                    String thisString = (String) retVal;
                    int index = thisString.indexOf('@');
                    String thisClass = thisString.substring(0, index);
                    String thisHash = thisString.substring(index + 1);
                    if (implementsInterface(thisClass, STATEMENT_INTERFACE)) {
                        assert st != null;
                        statements.put(thisHash, st);
                    }
                }
                currentObject.remove(ti);
            }
            batchNotEmpty = true;
        }
    }
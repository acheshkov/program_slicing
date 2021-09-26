void initialDataLoad() {
        assert (! SwingUtilities.isEventDispatchThread()) : "Must be called off the EDT!";

        /**
         * Wrap initializing the SQL result into a runnable. This makes it
         * possible to wait for the result in the main thread and cancel the
         * running statement from the main thread.
         *
         * If no statement is run - Thread.interrupted is checked at critical
         * points and allows us to do an early exit.
         *
         * See #159929.
         */
        class Loader implements Runnable, Cancellable {
            // Indicate whether the execution is finished
            private boolean finished = false;
            private Connection conn = null;
            private Statement stmt = null;
            private Thread loaderThread = null;

            @Override
            public void run() {
                loaderThread = Thread.currentThread();
                try {
                    DatabaseConnection dc = dataView.getDatabaseConnection();
                    conn = DBConnectionFactory.getInstance().getConnection(dc);
                    checkNonNullConnection(conn);
                    checkSupportForMultipleResultSets(conn);
                    DBMetaDataFactory dbMeta = new DBMetaDataFactory(conn);
                    limitSupported = dbMeta.supportsLimit();
                    String sql = dataView.getSQLString();
                    boolean isSelect = isSelectStatement(sql);

                    updateScrollableSupport(conn, dc, sql);

                    if (Thread.interrupted()) {
                        throw new InterruptedException();
                    }
                    
                    stmt = prepareSQLStatement(conn, sql);

                    if (Thread.interrupted()) {
                        throw new InterruptedException();
                    }
                    
                    boolean isResultSet = executeSQLStatementForExtraction(stmt, sql);

                    int updateCount = -1;
                    if(! isResultSet) {
                        updateCount = stmt.getUpdateCount();
                    }
                    
                    if (Thread.interrupted()) {
                        throw new InterruptedException();
                    }

                    ResultSet rs;

                    while (true) {
                        if (isResultSet) {
                            rs = stmt.getResultSet();

                            Collection<DBTable> tables = dbMeta.generateDBTables(rs, sql, isSelect);
                            DataViewDBTable dvTable = new DataViewDBTable(tables);
                            DataViewPageContext pageContext = dataView.addPageContext(dvTable);

                            loadDataFrom(pageContext, rs);

                            DataViewUtils.closeResources(rs);

                            dbMeta.postprocessTables(tables);
                        } else {
                            synchronized (dataView) {
                                dataView.addUpdateCount(updateCount);
                            }
                        }
                        if (supportesMultipleResultSets) {
                            isResultSet = stmt.getMoreResults();
                            updateCount = stmt.getUpdateCount();
                            if (isResultSet == false && updateCount == -1) {
                                break;
                            }
                        } else {
                            break;
                        }
                    }
                } catch (final SQLException | RuntimeException sqlEx) {
                    try {
                        SwingUtilities.invokeAndWait(new Runnable() {
                            @Override
                            public void run() {
                                dataView.setErrorStatusText(conn, stmt, sqlEx);
                            }
                        });
                    } catch (InterruptedException | InvocationTargetException ex) {
                        assert false;
                        // Ok - we were denied access to Swing EDT
                    }
                } catch (InterruptedException ex) {
                    // Expected when interrupted while waiting to get enter to
                    // the swing EDT
                } finally {
                    loaderThread = null;
                    DataViewUtils.closeResources(stmt);
                    synchronized (Loader.this) {
                        finished = true;
                        this.notifyAll();
                    }
                }
            }

            @Override
            public boolean cancel() {
                if (stmt != null) {
                    try {
                        stmt.cancel();
                    } catch (SQLException sqlEx) {
                        LOGGER.log(Level.FINE, null, sqlEx);
                        // Ok! The DBMS might not support Statement-Canceling
                    }
                }
                if(loaderThread != null) {
                    try {
                        loaderThread.interrupt();
                    } catch (NullPointerException ex) {
                        // Ignore - the call was finished between checking 
                        // loaderThread an calling interrupt on it.
                    }
                }
                return true;
            }

            /**
             * Check that the connection is not null. If it is null, try to find
             * cause of the failure and throw an exception.
             */
            private void checkNonNullConnection(Connection conn) throws
                    SQLException {
                if (conn == null) {
                    String msg;
                    Throwable t = DBConnectionFactory.getInstance()
                            .getLastException();
                    if (t != null) {
                        msg = t.getMessage();
                    } else {
                        msg = NbBundle.getMessage(SQLExecutionHelper.class,
                                "MSG_connection_failure", //NOI18N
                                dataView.getDatabaseConnection());
                    }
                    NotifyDescriptor nd = new NotifyDescriptor.Message(msg,
                            NotifyDescriptor.ERROR_MESSAGE);
                    DialogDisplayer.getDefault().notifyLater(nd);
                    LOGGER.log(Level.INFO, msg, t);
                    throw new SQLException(msg, t);
                }
            }

            private void checkSupportForMultipleResultSets(Connection conn) {
                try {
                    supportesMultipleResultSets = conn.getMetaData().supportsMultipleResultSets();
                } catch (SQLException | RuntimeException e) {
                    LOGGER.log(Level.INFO, "Database driver throws exception "  //NOI18N
                            + "when checking for multiple resultset support."); //NOI18N
                    LOGGER.log(Level.FINE, null, e);
                }
            }
        }
        Loader loader = new Loader();
        Future<?> f = rp.submit(loader);
        try {
            f.get();
        } catch (InterruptedException ex) {
            f.cancel(true);
        } catch (ExecutionException ex) {
            throw new RuntimeException(ex.getCause());
        }
        synchronized (loader) {
            while (true) {
                if (!loader.finished) {
                    try {
                        loader.wait();
                    } catch (InterruptedException ex) {
                    }
                } else {
                    break;
                }
            }
        }
    }
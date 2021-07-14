        public void propertyChange (PropertyChangeEvent e) {
            //System.err.println("ThreadsTreeModel.propertyChange("+e+")");
            //System.err.println("    "+e.getPropertyName()+", "+e.getOldValue()+" => "+e.getNewValue());
            ThreadGroupReference tg;
            if (e.getPropertyName() == ThreadsCache.PROP_THREAD_STARTED) {
                ThreadReference t = (ThreadReference) e.getNewValue();
                try {
                    tg = ThreadReferenceWrapper.threadGroup(t);
                } catch (InternalExceptionWrapper ex) {
                    tg = null;
                } catch (VMDisconnectedExceptionWrapper ex) {
                    return ;
                } catch (ObjectCollectedExceptionWrapper ex) {
                    return ;
                } catch (IllegalThreadStateExceptionWrapper ex) {
                    tg = null;
                }
            } else if (e.getPropertyName() == ThreadsCache.PROP_THREAD_DIED) {
                ThreadReference t = (ThreadReference) e.getOldValue();
                try {
                    tg = ThreadReferenceWrapper.threadGroup(t);
                } catch (InternalExceptionWrapper ex) {
                    tg = null;
                } catch (VMDisconnectedExceptionWrapper ex) {
                    return ;
                } catch (ObjectCollectedExceptionWrapper ex) {
                    tg = null;
                } catch (IllegalThreadStateExceptionWrapper ex) {
                    tg = null;
                }
            } else if (e.getPropertyName() == ThreadsCache.PROP_GROUP_ADDED) {
                tg = (ThreadGroupReference) e.getNewValue();
                try {
                    tg = ThreadGroupReferenceWrapper.parent(tg);
                } catch (InternalExceptionWrapper ex) {
                    tg = null;
                } catch (VMDisconnectedExceptionWrapper ex) {
                    tg = null;
                } catch (ObjectCollectedExceptionWrapper ex) {
                    tg = null;
                }
            } else {
                return ;
            }
            Object node;
            if (tg == null) {
                node = ROOT;
            } else {
                node = debugger.getThreadGroup(tg);
            }
            synchronized (this) {
                if (task == null) {
                    task = createTask();
                }
                if (nodesToRefresh == null) {
                    nodesToRefresh = new LinkedHashSet<Object>();
                }
                nodesToRefresh.add(node);
                task.schedule(100);
            }
        }
@Messages("EXC_CannotHaveNullRootContext=Cannot have null root context.")
    public final void setRootContext(final Node value) {
        if (value == null) {
            throw new IllegalArgumentException(EXC_CannotHaveNullRootContext());
        }

        synchronized (LOCK) {
            // a quick check if the context changes, in that case it's not necessary 
            // to acquire Children.MUTEX read lock
            if (rootContext.equals(value)) {
                return;
            }
        }

        // now lock first Children.MUTEX and the private lock afterwards, someone
        // might already have locked the Children.MUTEX
        class SetRootContext implements Runnable {
            @Override
            public void run() {
                synchronized (LOCK) {
                    if (rootContext.equals(value)) {
                        return;
                    }
                    addRemoveListeners(false);
                    Node oldValue = rootContext;
                    rootContext = value;

                    oldValue.removeNodeListener(weakListener);
                    rootContext.addNodeListener(weakListener);

                    fireInAWT(PROP_ROOT_CONTEXT, oldValue, rootContext);

                    Node[] newselection = getSelectedNodes();

                    if (!areUnderTarget(newselection, rootContext)) {
                        newselection = new Node[0];
                    }
                    setExploredContext(rootContext, newselection);
                }
            }
        }

        SetRootContext run = new SetRootContext();
        Children.MUTEX.readAccess(run);
    }
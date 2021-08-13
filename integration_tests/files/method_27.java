    public IStatus applyDeltas(Collection<ModelDelta> deltas, String[] filters) {
        if (filters == null) {
            filters = new String[0];
        }

        MultiStatus multiStatus = new MultiStatus(Activator.PI_WORKBENCH, 0, "", null); //$NON-NLS-1$
        LinkedList<ModelDelta> delayedDeltas = new LinkedList<ModelDelta>();

        deltaIterationLoop: for (final ModelDelta delta : deltas) {
            for (String filter : filters) {
                if (delta.getAttributeName().equals(filter)) {
                    continue deltaIterationLoop;
                }
            }

            final IStatus[] status = new IStatus[1];
            SafeRunner.run(new ISafeRunnable() {
                public void run() throws Exception {
                    status[0] = delta.apply();
                }

                public void handleException(Throwable exception) {
                    status[0] = new Status(IStatus.ERROR, Activator.PI_WORKBENCH,
                            "Failed to apply delta", exception); //$NON-NLS-1$
                }
            });

            if (status[0].getSeverity() == IStatus.CANCEL) {
                delayedDeltas.add(delta);
                continue;
            }
            multiStatus.add(status[0]);

            switch (status[0].getCode()) {
            case IStatus.INFO:
                logger.info(status[0].getMessage());
                break;
            case IStatus.WARNING:
                logger.warn(status[0].getMessage());
                break;
            case IStatus.ERROR:
                logger.error(status[0].getMessage());
                break;
            }
        }

        for (Iterator<ModelDelta> it = delayedDeltas.iterator(); it.hasNext();) {
            final ModelDelta delta = it.next();
            final IStatus[] status = new IStatus[1];
            SafeRunner.run(new ISafeRunnable() {
                public void run() throws Exception {
                    status[0] = delta.apply();
                }

                public void handleException(Throwable exception) {
                    status[0] = new Status(IStatus.ERROR, Activator.PI_WORKBENCH,
                            "Failed to apply delta", exception); //$NON-NLS-1$
                }
            });

            if (status[0].getSeverity() == IStatus.CANCEL) {
                continue;
            }

            multiStatus.add(status[0]);

            switch (status[0].getCode()) {
            case IStatus.INFO:
                logger.info(status[0].getMessage());
                break;
            case IStatus.WARNING:
                logger.warn(status[0].getMessage());
                break;
            case IStatus.ERROR:
                logger.error(status[0].getMessage());
                break;
            }
        }

        return multiStatus;
    }

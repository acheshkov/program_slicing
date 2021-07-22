    public void freeEntry(BasicPoolEntry entry, boolean reusable, long validDuration, TimeUnit timeUnit) {

        HttpRoute route = entry.getPlannedRoute();
        if (log.isDebugEnabled()) {
            log.debug("Releasing connection" +
                    " [" + route + "][" + entry.getState() + "]");
        }

        poolLock.lock();
        try {
            if (shutdown) {
                // the pool is shut down, release the
                // connection's resources and get out of here
                closeConnection(entry);
                return;
            }

            // no longer issued, we keep a hard reference now
            leasedConnections.remove(entry);

            RouteSpecificPool rospl = getRoutePool(route, true);

            if (reusable) {
                if (log.isDebugEnabled()) {
                    String s;
                    if (validDuration > 0) {
                        s = "for " + validDuration + " " + timeUnit;
                    } else {
                        s = "indefinitely";
                    }
                    log.debug("Pooling connection" +
                            " [" + route + "][" + entry.getState() + "]; keep alive " + s);
                }
                rospl.freeEntry(entry);
                entry.updateExpiry(validDuration, timeUnit);
                freeConnections.add(entry);
            } else {
                rospl.dropEntry();
                numConnections--;
            }

            notifyWaitingThread(rospl);

        } finally {
            poolLock.unlock();
        }
    }
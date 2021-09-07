protected final void binaryScanStarted(
                @NonNull final URL root,
                final boolean upToDate,
                @NonNull final LinkedHashMap<BinaryIndexerFactory, Context> contexts,
                @NonNull final BitSet startedIndexers) throws IOException {
            int index = 0;
            for(Map.Entry<BinaryIndexerFactory,Context> e : contexts.entrySet()) {
                final Context ctx = e.getValue();
                final BinaryIndexerFactory bif = e.getKey();
                SPIAccessor.getInstance().setAllFilesJob(ctx, !upToDate);
                parkWhileSuspended();
                long st = System.currentTimeMillis();
                logStartIndexer(bif.getIndexerName());
                boolean vote;
                try {
                    startedIndexers.set(index);
                    vote = bif.scanStarted(ctx);
                } catch (Throwable t) {
                    if (t instanceof ThreadDeath) {
                        throw (ThreadDeath) t;
                    } else {
                        vote = false;
                        Exceptions.printStackTrace(t);
                    }
                }
                long et = System.currentTimeMillis();
                logIndexerTime(bif.getIndexerName(), (int)(et-st));
                if (!vote) {
                    SPIAccessor.getInstance().setAllFilesJob(ctx, true);
                }
                index++;
            }
        }
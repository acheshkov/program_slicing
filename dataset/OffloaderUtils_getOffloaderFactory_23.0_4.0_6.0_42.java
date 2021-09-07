static Pair<NarClassLoader, LedgerOffloaderFactory> getOffloaderFactory(String narPath) throws IOException {
        // need to load offloader NAR to the classloader that also loaded LedgerOffloaderFactory in case
        // LedgerOffloaderFactory is loaded by a classloader that is not the default classloader
        // as is the case for the pulsar presto plugin
        NarClassLoader ncl = NarClassLoader.getFromArchive(new File(narPath), Collections.emptySet(), LedgerOffloaderFactory.class.getClassLoader());
        String configStr = ncl.getServiceDefinition(PULSAR_OFFLOADER_SERVICE_NAME);

        OffloaderDefinition conf = ObjectMapperFactory.getThreadLocalYaml()
            .readValue(configStr, OffloaderDefinition.class);
        if (StringUtils.isEmpty(conf.getOffloaderFactoryClass())) {
            throw new IOException(
                String.format("The '%s' offloader does not provide an offloader factory implementation",
                    conf.getName()));
        }

        try {
            // Try to load offloader factory class and check it implements Offloader interface
            Class factoryClass = ncl.loadClass(conf.getOffloaderFactoryClass());
            CompletableFuture<LedgerOffloaderFactory> loadFuture = new CompletableFuture<>();
            Thread loadingThread = new Thread(() -> {
                Thread.currentThread().setContextClassLoader(ncl);
                try {
                    Object offloader = factoryClass.newInstance();
                    if (!(offloader instanceof LedgerOffloaderFactory)) {
                        throw new IOException("Class " + conf.getOffloaderFactoryClass() + " does not implement interface "
                            + LedgerOffloaderFactory.class.getName());
                    }
                    loadFuture.complete((LedgerOffloaderFactory) offloader);
                } catch (Throwable t) {
                    loadFuture.completeExceptionally(t);
                }
            }, "load-factory-" + factoryClass);
            try {
                loadingThread.start();
                return Pair.of(ncl, loadFuture.get());
            } finally {
                loadingThread.join();
            }
        } catch (Throwable t) {
            rethrowIOException(t);
        }
        return null;
    }
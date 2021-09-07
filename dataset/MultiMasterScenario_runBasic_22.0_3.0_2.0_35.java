public void runBasic() throws Exception {
        logger.info("\n####################################################");
        logger.info("Basic Active-Active");
        logger.info("####################################################");

        logger.info("1) Starting insert loops across multiple regions ...");

        List<Mono<Void>> basicTask = new ArrayList<>();

        int documentsToInsertPerWorker = 100;

        for (Worker worker : this.workers) {
            basicTask.add(worker.runLoopAsync(documentsToInsertPerWorker));
        }

        Mono.when(basicTask).block();

        basicTask.clear();

        logger.info("2) Reading from every region ...");

        int expectedDocuments = this.workers.size() * documentsToInsertPerWorker;
        for (Worker worker : this.workers) {
            basicTask.add(worker.readAllAsync(expectedDocuments));
        }

        Mono.when(basicTask).block();

        basicTask.clear();

        logger.info("3) Deleting all the documents ...");

        this.workers.get(0).deleteAll();

        logger.info("####################################################");
    }
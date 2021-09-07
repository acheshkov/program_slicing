private void diff(Map<String, IndexerInfo<T>> lastKnownInfos, Map<String, Set<IndexerInfo<T>>> currentInfosMap, Map<String, Set<IndexerInfo<T>>> addedOrChangedInfosMap) {
        for(String indexerName : currentInfosMap.keySet()) {
            if (!lastKnownInfos.containsKey(indexerName)) {
                addedOrChangedInfosMap.put(indexerName, currentInfosMap.get(indexerName));
            } else {
                IndexerInfo<T> lastKnownInfo = lastKnownInfos.get(indexerName);
                Set<IndexerInfo<T>> currentInfos = currentInfosMap.get(indexerName);

                // check versions
                for(IndexerInfo<T> currentInfo : currentInfos) {
                    if (lastKnownInfo.getIndexerVersion() != currentInfo.getIndexerVersion()) {
                        Set<IndexerInfo<T>> addedOrChangedInfos = addedOrChangedInfosMap.get(indexerName);
                        if (addedOrChangedInfos == null) {
                            addedOrChangedInfos = new HashSet<IndexerInfo<T>>();
                            addedOrChangedInfosMap.put(indexerName, addedOrChangedInfos);
                        }
                        addedOrChangedInfos.add(currentInfo);
                    }
                }

                // check mimetypes
                for(IndexerInfo<T> currentInfo : currentInfos) {
                    if (!lastKnownInfo.getMimeTypes().containsAll(currentInfo.getMimeTypes())) {
                        Set<IndexerInfo<T>> addedOrChangedInfos = addedOrChangedInfosMap.get(indexerName);
                        if (addedOrChangedInfos == null) {
                            addedOrChangedInfos = new HashSet<IndexerInfo<T>>();
                            addedOrChangedInfosMap.put(indexerName, addedOrChangedInfos);
                        }
                        addedOrChangedInfos.add(currentInfo);
                    }
                }
            }
        }
    }
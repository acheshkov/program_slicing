private void insert(KuduMappingConfig config, Dml dml) {
        KuduMappingConfig.KuduMapping kuduMapping = config.getKuduMapping();
        String configTable = kuduMapping.getTable();
        String configDatabase = kuduMapping.getDatabase();
        String table = dml.getTable();
        String database = dml.getDatabase();
        if (configTable.equals(table) && configDatabase.equals(database)) {
            List<Map<String, Object>> data = dml.getData();
            if (data == null || data.isEmpty()) {
                return;
            }
            try {
                int idx = 1;
                boolean completed = false;
                List<Map<String, Object>> dataList = new ArrayList<>();

                for (Map<String, Object> entry : data) {
                    dataList.add(entry);
                    idx++;
                    if (idx % kuduMapping.getCommitBatch() == 0) {
                        kuduTemplate.insert(kuduMapping.getTargetTable(), dataList);
                        dataList.clear();
                        completed = true;
                    }
                }
                if (!completed) {
                    kuduTemplate.insert(kuduMapping.getTargetTable(), dataList);
                }
            } catch (KuduException e) {
                logger.error(e.getMessage());
                logger.error("DML: {}", JSON.toJSONString(dml, SerializerFeature.WriteMapNullValue));
            }
        }
    }
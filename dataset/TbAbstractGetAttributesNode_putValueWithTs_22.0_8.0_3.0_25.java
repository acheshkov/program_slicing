private void putValueWithTs(TbMsg msg, TsKvEntry r) {
        ObjectNode value = mapper.createObjectNode();
        value.put(TS, r.getTs());
        switch (r.getDataType()) {
            case STRING:
                value.put(VALUE, r.getValueAsString());
                break;
            case LONG:
                value.put(VALUE, r.getLongValue().get());
                break;
            case BOOLEAN:
                value.put(VALUE, r.getBooleanValue().get());
                break;
            case DOUBLE:
                value.put(VALUE, r.getDoubleValue().get());
                break;
            case JSON:
                try {
                    value.set(VALUE, mapper.readTree(r.getJsonValue().get()));
                } catch (IOException e) {
                    throw new JsonParseException("Can't parse jsonValue: " + r.getJsonValue().get(), e);
                }
                break;
        }
        msg.getMetaData().putValue(r.getKey(), value.toString());
    }
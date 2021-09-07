@Override
    protected void doXContent(XContentBuilder builder, Params params) throws IOException {
        builder.startObject(getWriteableName());

        builder.startObject(fieldName);

        if (shape != null) {
            builder.field(SHAPE_FIELD.getPreferredName());
            GeoJson.toXContent(shape, builder, params);
        } else {
            builder.startObject(INDEXED_SHAPE_FIELD.getPreferredName())
                .field(SHAPE_ID_FIELD.getPreferredName(), indexedShapeId);
            if (indexedShapeIndex != null) {
                builder.field(SHAPE_INDEX_FIELD.getPreferredName(), indexedShapeIndex);
            }
            if (indexedShapePath != null) {
                builder.field(SHAPE_PATH_FIELD.getPreferredName(), indexedShapePath);
            }
            if (indexedShapeRouting != null) {
                builder.field(SHAPE_ROUTING_FIELD.getPreferredName(), indexedShapeRouting);
            }
            builder.endObject();
        }

        if(relation != null) {
            builder.field(RELATION_FIELD.getPreferredName(), relation.getRelationName());
        }

        doShapeQueryXContent(builder, params);
        builder.endObject();
        builder.field(IGNORE_UNMAPPED_FIELD.getPreferredName(), ignoreUnmapped);

        printBoostAndQueryName(builder);

        builder.endObject();
    }
private void processProducesConsumes(CodegenOperation op) {
        if (!(Boolean) op.vendorExtensions.get(X_HAS_BODY_OR_FORM_PARAM)) {
            SetNoContent(op, X_INLINE_CONTENT_TYPE); // TODO: 5.0 Remove
            SetNoContent(op, VENDOR_EXTENSION_X_INLINE_CONTENT_TYPE);
        }
        if (op.hasConsumes) {
            // deduplicate
            Map<String, Map<String, String>> consumes = new HashMap<>();
            for (Map<String, String> m : op.consumes) {
                consumes.put(m.get(MEDIA_TYPE), m);
            }
            op.consumes = new ArrayList<>(consumes.values());

            // add metadata
            for (Map<String, String> m : op.consumes) {
                processMediaType(op, m);
                processInlineConsumesContentType(op, m);

            }
            if (isMultipartOperation(op.consumes)) {
                op.isMultipart = Boolean.TRUE;
            }
        }
        if (op.hasProduces) {
            // deduplicate
            Map<String, Map<String, String>> produces = new HashMap<>();
            for (Map<String, String> m : op.produces) {
                produces.put(m.get(MEDIA_TYPE), m);
            }
            op.produces = new ArrayList<>(produces.values());

            // add metadata
            for (Map<String, String> m : op.produces) {
                processMediaType(op, m);
                processInlineProducesContentType(op, m);
            }
        }
    }
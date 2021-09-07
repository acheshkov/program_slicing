@NbBundle.Messages({
        "ERR_duplicateIdentifier=Instance has duplicate fx:id",
        "# {0} - tag name",
        "ERR_defineMustProvideId=Missing fx:id attribute on {0} inside fx:define block"
    })
    @Override
    protected void visitBaseInstance(FxInstance i) {
        if (i.getId() == null) {
            // check if the instance is not directly inside 'define' node:
            if (parentNode != null && parentNode.getKind() == FxNode.Kind.Element &&
                "define".equals(parentNode.getSourceName())) {
                TextPositions pos = env.getTreeUtilities().positions(i);
                env.addError(new ErrorMark(
                    pos.getStart(), pos.getContentStart() - pos.getStart(),
                    "define-must-provide-id",
                    ERR_defineMustProvideId(i.getSourceName()),
                    i
                ));
            }
            super.visitBaseInstance(i);
            return;
        }
        if (instances == null) {
            instances = Collections.singletonMap(i.getId(), i);
        } else {
            Map<String, FxInstance> newInstances;
            
            if (instances.size() == 1) {
                newInstances = new HashMap<String, FxInstance>();
                newInstances.putAll(instances);
                instances = newInstances;
            } else {
                newInstances = instances;
            }
            if (newInstances.containsKey(i.getId())) {
                TextPositions pos = env.getTreeUtilities().positions(i);
                // error, duplicate ID found.
                env.addError(new ErrorMark(
                    pos.getStart(), pos.getContentStart() - pos.getStart(),
                    "duplicate-id",
                    ERR_duplicateIdentifier(),
                    i
                ));
            } else {
                newInstances.put(i.getId(), i);
            }
        }
        super.visitBaseInstance(i);
    }
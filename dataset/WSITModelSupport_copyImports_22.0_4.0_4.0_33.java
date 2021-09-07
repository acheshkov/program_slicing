static void copyImports(final WSDLModel model, final FileObject srcFolder, Collection<FileObject> createdFiles) throws CatalogModelException {
        
        FileObject modelFO = Utilities.getFileObject(model.getModelSource());
        
        try {
            FileObject configFO = FileUtil.copyFile(modelFO, srcFolder, modelFO.getName(), CONFIG_WSDL_EXTENSION);
            if (createdFiles != null) {
                createdFiles.add(configFO);
            }
            
            WSDLModel newModel = getModelFromFO(configFO, true);
            
            removePolicies(newModel);
            removeTypes(newModel);
            
            Collection<Import> oldImports = model.getDefinitions().getImports();
            Collection<Import> newImports = newModel.getDefinitions().getImports();
            Iterator<Import> newImportsIt = newImports.iterator();
            for (Import i : oldImports) {
                WSDLModel oldImportedModel = i.getImportedWSDLModel();
                FileObject oldImportFO = Utilities.getFileObject(oldImportedModel.getModelSource());
                newModel.startTransaction();
                try {
                    newImportsIt.next().setLocation(oldImportFO.getName() + "." + CONFIG_WSDL_EXTENSION);
                } finally {
                    newModel.endTransaction();
                }
                copyImports(oldImportedModel, srcFolder, createdFiles);
            }
        } catch (IOException e) {
            // ignore - this happens when files are imported recursively
            logger.log(Level.FINE, null, e);
        }
    }
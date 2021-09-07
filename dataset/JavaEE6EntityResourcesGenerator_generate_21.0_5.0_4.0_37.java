@Override
    public Set<FileObject> generate(ProgressHandle pHandle) throws IOException {
        if (pHandle != null) {
            initProgressReporting(pHandle);
        }

        createFolders( false);

        //Make necessary changes to the persistence.xml
        new PersistenceHelper(getProject()).configure(getModel().getBuilder().
                getAllEntityNames(),!RestUtils.hasJTASupport(getProject()));
        
        Set<String> entities = new HashSet<String>();
        for (EntityClassInfo info : getModel().getEntityInfos()) {
            String entity = info.getEntityFqn();
            entities.add( entity );
            Util.modifyEntity( entity , getProject());
        }
        
        FileObject targetResourceFolder = null;
        SourceGroup[] sourceGroups = SourceGroupSupport.getJavaSourceGroups(getProject());
        SourceGroup targetSourceGroup = SourceGroupSupport.findSourceGroupForFile(
                sourceGroups, getTargetFolder());
        if (targetSourceGroup != null) {
            targetResourceFolder = SourceGroupSupport.getFolderForPackage(
                    targetSourceGroup, getResourcePackageName(), true);
        }
        if (targetResourceFolder == null) {
            targetResourceFolder = getTargetFolder();
        }
        
        Util.generateRESTFacades(getProject(), entities, getModel(), 
                targetResourceFolder, getResourcePackageName());
        
        finishProgressReporting();

        return new HashSet<FileObject>();
    }
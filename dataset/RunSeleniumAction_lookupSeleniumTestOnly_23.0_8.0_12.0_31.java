@CheckForNull
    private FileObject[] lookupSeleniumTestOnly(Lookup context) {
        Collection<? extends FileObject> fileObjects = context.lookupAll(FileObject.class);
        if (fileObjects.isEmpty()) {
            return null;
        }
        Project p = null;
        Iterator<? extends FileObject> iterator = fileObjects.iterator();
        while (iterator.hasNext()) {
            FileObject fo = iterator.next();
            Project project = FileOwnerQuery.getOwner(fo);
            if (project == null) {
                return null;
            }
            if(p == null) {
                p = project;
            }
            if(!p.equals(project)) { // selected FileObjects belong to different projects
                return null;
            }
            Sources sources = ProjectUtils.getSources(project);
            SourceGroup[] sourceGroups = sources.getSourceGroups(WebClientProjectConstants.SOURCES_TYPE_HTML5_TEST_SELENIUM);
            if (sourceGroups.length != 1) { // no Selenium Tests Folder set yet
                return null;
            }
            FileObject rootFolder = sourceGroups[0].getRootFolder();
            if (!FileUtil.isParentOf(rootFolder, fo)) { // file in not under Selenium Tests Folder
                return null;
            }
        }
        return fileObjects.toArray(new FileObject[fileObjects.size()]);
    }
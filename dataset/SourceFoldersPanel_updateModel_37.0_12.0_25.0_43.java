private void updateModel(List<SourceFolder> srcFolders) {
        if (srcFolders.isEmpty()) {
            return;
        }
        List<SourceFolder> finalSourceFolders = new ArrayList<SourceFolder>();
        List<SourceFolder> finalTestFolders = new ArrayList<SourceFolder>();
        boolean notEmpty = false;
        for (SourceFolder sf : srcFolders) {
            boolean contains = false;
            for (SourceFolder msf : model.getSourceFolders()) {
                if (msf.location.equals(sf.location)) {
                    contains = true;
                    break;
                }
            }
            if (!contains) {
                boolean testFolder = false;
                for (String path : TEST_FOLDER_PATHS) {
                    if (sf.location.indexOf(path) != -1) {
                        testFolder = true;
                        break;
                    }
                }
                if (!testFolder) {
                    finalSourceFolders.add(sf);
                    notEmpty = true;
                } else {
                    finalTestFolders.add(sf);
                    notEmpty = true;
                }
            }
        }
        if (notEmpty) {
            FolderComparator comparator = new FolderComparator();
            Collections.sort(finalSourceFolders, comparator);
            Collections.sort(finalTestFolders, comparator);
            for (SourceFolder sf : finalSourceFolders) {
                model.addSourceFolder(sf, false);
            }
            for (SourceFolder sf : finalTestFolders) {
                model.addSourceFolder(sf, true);
            }
        }
    }
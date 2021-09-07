final void refresh() {
        synchronized (resourceUris) {
            List<Resource> resources = new ArrayList<Resource>();
            resources.addAll(nbproject.getMavenProject().getResources());
            resources.addAll(nbproject.getMavenProject().getTestResources());
            Set<File> old = new HashSet<File>(resourceUris);
            Set<File> added = new HashSet<File>();
            
                for (Resource res : resources) {
                    String dir = res.getDirectory();
                    if (dir == null) {
                        continue;
                    }
                    URI uri = FileUtilities.getDirURI(project.getProjectDirectory(), dir);
                    File file = Utilities.toFile(uri);
                    if (!old.contains(file) && !added.contains(file)) { // if a given file is there multiple times, we get assertion back from FileUtil. there can be only one listener+file tuple
                        FileUtil.addRecursiveListener(this, file);
                    }
                    added.add(file);
                }
            
            old.removeAll(added);
            for (File oldFile : old) {
                FileUtil.removeRecursiveListener(this, oldFile);
            }
            resourceUris.removeAll(old);
            resourceUris.addAll(added);
        }
    }
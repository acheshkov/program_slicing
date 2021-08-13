protected static void loadPackageDirectory(File directory, boolean verbose)
      throws Exception {
    File[] contents = directory.listFiles();

    // make sure that jar files and lib directory get processed first
    for (int i = 0; i < contents.length; i++) {
        if (contents[i].isFile() && contents[i].getPath().endsWith(".jar")) {
            if (verbose) {
              System.out.println("[Weka] loading " + contents[i].getPath());
            }
            ClassloaderUtil.addFile(contents[i].getPath());
        } else if (contents[i].isDirectory()
            && contents[i].getName().equalsIgnoreCase("lib")) {
            loadPackageDirectory(contents[i], verbose);
        }
    }

    // now any auxilliary files
    for (int i = 0; i < contents.length; i++) {
        if (contents[i].isFile() && contents[i].getPath().endsWith("Beans.props")) {
            KnowledgeFlowApp.addToPluginBeanProps(contents[i]);
            KnowledgeFlowApp.disposeSingleton();

        } else if (contents[i].isFile()
            && contents[i].getPath().endsWith("Explorer.props")) {
            processExplorerProps(contents[i]);
        } else if (contents[i].isFile()
            && contents[i].getPath().endsWith("GUIEditors.props")) {
            processGUIEditorsProps(contents[i]);
        } else if (contents[i].isFile()
            && contents[i].getPath().endsWith("GenericPropertiesCreator.props")) {
            processGenericPropertiesCreatorProps(contents[i]);
        } else if (contents[i].isFile()
            && contents[i].getPath().endsWith("PluginManager.props")) {
            processPluginManagerProps(contents[i]);
        }
    }
}
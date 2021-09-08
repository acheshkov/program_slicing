@Override public Map<String, String> createReplacements(String actionName, Lookup lookup) {
        FileObject[] fos = extractFileObjectsfromLookup(lookup);
        SourceGroup group = findGroup(ProjectUtils.getSources(project).getSourceGroups(JavaProjectConstants.SOURCES_TYPE_JAVA), fos);
        HashMap<String, String> replaceMap = new HashMap<String, String>();
        // read environment variables in the IDE and prefix them with "env." just in case someone uses it as variable in the action mappings
        for (Map.Entry<String, String> entry : System.getenv().entrySet()) {
            replaceMap.put(MavenCommandLineExecutor.ENV_PREFIX + entry.getKey(), entry.getValue());
        }
        
        if (fos.length > 0) {
            replaceMap.put(ABSOLUTE_PATH, FileUtil.toFile(fos[0]).getAbsolutePath());
        }
        
        //read global variables defined in the IDE
        Map<String, String> vars = readVariables();
        replaceMap.putAll(vars);
        
        //read active configuration properties..
        Map<String, String> configProps = project.getLookup().lookup(M2ConfigProvider.class).getActiveConfiguration().getProperties();
        replaceMap.putAll(configProps);

        NbMavenProject prj = project.getLookup().lookup(NbMavenProject.class);
        replaceMap.put(GROUPID, prj.getMavenProject().getGroupId());
        replaceMap.put(ARTIFACTID, prj.getMavenProject().getArtifactId());

        StringBuilder packClassname = new StringBuilder();
        StringBuilder classname = new StringBuilder();
        StringBuilder classnameExt = new StringBuilder();
        if (group != null) {
            boolean first = true;
            boolean isTest = false;
            Set<String> uniqueClassNames = new HashSet<String>(fos.length);
            for (FileObject file : fos) {
                if (first) {
                    first = false;
                } else {
                    if (!isTest && !(ActionProvider.COMMAND_TEST_SINGLE.equals(actionName) ||
                                     ActionProvider.COMMAND_DEBUG_TEST_SINGLE.equals(actionName) ||
                                     ActionProvider.COMMAND_PROFILE_TEST_SINGLE.equals(actionName) ||
                                     ActionProvider.COMMAND_TEST.equals(actionName))) {
                        // Execution can not have more files separated by commas. Only test can.
                        break;
                    } else {
                        isTest = true;
                    }
                    packClassname.append(',');
                    classname.append(',');
                    classnameExt.append(',');
                }
                if (file.isFolder()) {
                    String rel = FileUtil.getRelativePath(group.getRootFolder(), file);
                    assert rel != null;
                    String pkg = rel.replace('/', '.');
                    if (!pkg.isEmpty()) {
                        packClassname.append(pkg).append(".**."); // test everything under this package recusively
                    }
                    packClassname.append("*");
                    if (ActionProvider.COMMAND_TEST_SINGLE.equals(actionName) || ActionProvider.COMMAND_DEBUG_TEST_SINGLE.equals(actionName)) {
                        packClassname.append("Test");
                    }
                    classname.append(pkg); // ?
                    classnameExt.append(pkg); // ??
                } else { // XXX do we need to limit to text/x-java? What about files of other type?
                    String relP = FileUtil.getRelativePath(group.getRootFolder(), file.getParent());
                    assert relP != null;
                    StringBuilder cn = new StringBuilder();
                    if (!relP.isEmpty()) {
                        cn.append(relP.replace('/', '.')).append('.');
                    }
                    String n = file.getName();
                    cn.append(n);
                    if (uniqueClassNames.add(cn.toString())) {
                        packClassname.append(cn);
                        classname.append(n);
                    } else {
                        packClassname.deleteCharAt(packClassname.length() - 1); // Delete the comma
                        classname.deleteCharAt(classname.length() - 1);
                    }
                    classnameExt.append(file.getNameExt());
                    if (MavenSourcesImpl.NAME_SOURCE.equals(group.getName()) &&
                        (ActionProvider.COMMAND_TEST_SINGLE.equals(actionName) ||
                         ActionProvider.COMMAND_DEBUG_TEST_SINGLE.equals(actionName) ||
                         ActionProvider.COMMAND_PROFILE_TEST_SINGLE.equals(actionName))) {
                        String fix = "Test";
                        if (classnameExt.toString().endsWith("." + file.getExt())) {
                            classnameExt.delete(classnameExt.length() - ("." + file.getExt()).length(), classnameExt.length());
                            URL[] unitRoots = UnitTestForSourceQuery.findUnitTests(group.getRootFolder());
                            if (unitRoots != null) {
                                for (URL unitRoot : unitRoots) {
                                    FileObject root = URLMapper.findFileObject(unitRoot);
                                    if (root != null) { //#237312
                                        String ngPath = relP + (relP.isEmpty() ? "" : "/") + classnameExt + "NGTest." + file.getExt();
                                        if (root.getFileObject(ngPath) != null) {
                                            fix = "NGTest";
                                            break;
                                        }
                                    }
                                }
                            }
                            classnameExt.append(fix).append(".").append(file.getExt());
                        }
                        packClassname.append(fix);
                        classname.append(fix);
                    }
                }
            }
        } else {
            // not all of the selected files are under one source root, so maybe they were
            // selected from both source and test packages and "Test Files" action was invoked on them?
            if (ActionProvider.COMMAND_TEST_SINGLE.equals(actionName) ||
                ActionProvider.COMMAND_DEBUG_TEST_SINGLE.equals(actionName)) 
            {
                HashSet<String> test = new HashSet<String>();
                addSelectedFiles(false, fos, test);
                addSelectedFiles(true, fos, test);
                String files2test = test.toString().replace(" ", "");
                packClassname.append(files2test.substring(1, files2test.length() - 1));
            }
        }
        if (packClassname.length() > 0) { //#213671
            replaceMap.put(PACK_CLASSNAME, packClassname.toString());
        }
        if (classname.length() > 0) { //#213671
            replaceMap.put(CLASSNAME, classname.toString());
        }
        if (classnameExt.length() > 0) { //#213671
            replaceMap.put(CLASSNAME_EXT, classnameExt.toString());
        }

        Collection<? extends SingleMethod> methods = lookup.lookupAll(SingleMethod.class);
        if (methods.size() == 1) {
            //sort of hack to push the method name through the current apis..
            SingleMethod method = methods.iterator().next();
            replaceMap.put(METHOD_NAME, method.getMethodName());
        }

        if (group != null &&
                //TODO not nice, how to figure in a better way? by source classpath?
                (MavenSourcesImpl.NAME_TESTSOURCE.equals(group.getName()))) {
            replaceMap.put(CLASSPATHSCOPE,"test"); //NOI18N
        } else {
            replaceMap.put(CLASSPATHSCOPE,"runtime"); //NOI18N
        }
        return replaceMap;
    }
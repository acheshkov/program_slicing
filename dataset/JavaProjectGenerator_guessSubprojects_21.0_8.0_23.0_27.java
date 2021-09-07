public static List<String> guessSubprojects(PropertyEvaluator evaluator,
            List<JavaCompilationUnit> javaCompilationUnits, File projectBase, File freeformBase) {
        //assert ProjectManager.mutex().isReadAccess() || ProjectManager.mutex().isWriteAccess();
        Set<String> subprojs = new HashSet<String>();
        for (JavaCompilationUnit cu : javaCompilationUnits) {
            if (cu.classpath != null) {
                for (JavaCompilationUnit.CP cp : cu.classpath) {
                    if (!"compile".equals(cp.mode))  { // NOI18N
                        continue;
                    }
                    String classpath = evaluator.evaluate(cp.classpath);
                    if (classpath == null) {
                        continue;
                    }
                    for (String s : PropertyUtils.tokenizePath(classpath)) {
                        File file = FileUtil.normalizeFile(new File(s));
                        AntArtifact aa = AntArtifactQuery.findArtifactFromFile(file);
                        if (aa != null) {
                            File proj = FileUtil.toFile(aa.getProject().getProjectDirectory());
                            String p = Util.relativizeLocation(projectBase, freeformBase, proj);
                            subprojs.add(p);
                        }
                    }
                }
            }
        }
        return new ArrayList<String>(subprojs);
    }
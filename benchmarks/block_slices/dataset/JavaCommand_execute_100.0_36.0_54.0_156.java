@Override
  public Object execute(CommandLine commandLine)
    throws Exception
  {
    String projectName = commandLine.getValue(Options.PROJECT_OPTION);
    String mainClass = commandLine.getValue(Options.CLASSNAME_OPTION);
    boolean debug = commandLine.hasOption(Options.DEBUG_OPTION);
    String workingDir = commandLine.getValue(WORKINGDIR_OPTION);

    IProject project = ProjectUtils.getProject(projectName);
    project.build(IncrementalProjectBuilder.INCREMENTAL_BUILD, null);

    IJavaProject javaProject = JavaUtils.getJavaProject(project);

    Project antProject = new Project();
    BuildLogger buildLogger = new DefaultLogger();
    buildLogger.setMessageOutputLevel(debug ? Project.MSG_DEBUG : Project.MSG_INFO);
    buildLogger.setOutputPrintStream(getContext().out);
    buildLogger.setErrorPrintStream(getContext().err);
    antProject.addBuildListener(buildLogger);
    antProject.setBasedir(ProjectUtils.getPath(project));
    antProject.setDefaultInputStream(System.in);

    if (mainClass == null){
      mainClass =
        getPreferences().getValue(project, "org.eclim.java.run.mainclass");
    }

    if (mainClass == null ||
        mainClass.trim().equals(StringUtils.EMPTY) ||
        mainClass.trim().equals("none"))
    {
      // first try to locate a main method.
      mainClass = findMainClass(javaProject);
      if (mainClass == null){
        throw new RuntimeException(Services.getMessage(
              "setting.not.set", "org.eclim.java.run.mainclass"));
      }
    }

    if (mainClass.endsWith(".java") || mainClass.endsWith(".class")){
      mainClass = mainClass.substring(0, mainClass.lastIndexOf('.'));
    }

    // validate that the main class doesn't contain errors
    IType type = javaProject.findType(mainClass);
    if (type != null){
      ICompilationUnit src = type.getCompilationUnit();
      if (src != null){
        IProblem[] problems = JavaUtils.getProblems(src);
        for (IProblem problem : problems){
          if (problem.isError()){
            println(Services.getMessage("src.contains.errors"));
            return null;
          }
        }
      }
    }

    Java java = new MyJava();
    java.setTaskName("java");
    java.setProject(antProject);
    java.setClassname(mainClass);
    java.setFork(true);

    // use the project configured jvm if possible
    IVMInstall jvm = JavaRuntime.getVMInstall(javaProject);
    if (jvm != null){
      String path = jvm.getInstallLocation() + "/bin/java";
      if (new File(path).exists()){
        java.setJvm(path);
      }
    }

    if (workingDir != null){
      java.setDir(new File(workingDir));
    }

    // construct classpath
    Path classpath = new Path(antProject);
    String[] paths = ClasspathUtils.getClasspath(javaProject);
    for (String path : paths){
      Path.PathElement pe = classpath.createPathElement();
      pe.setPath(path);
    }

    java.setClasspath(classpath);

    // add default vm args
    String[] defaultArgs =
      getPreferences().getArrayValue(project, "org.eclim.java.run.jvmargs");
    for(String vmarg : defaultArgs){
      if (!vmarg.startsWith("-")){
        continue;
      }
      Argument a = java.createJvmarg();
      a.setValue(vmarg);
    }

    // add any supplied vm args
    String[] vmargs = commandLine.getValues(VMARGS_OPTION);
    if (vmargs != null && vmargs.length > 0){
      for(String vmarg : vmargs){
        if (!vmarg.startsWith("-")){
          continue;
        }
        Argument a = java.createJvmarg();
        a.setValue(vmarg);
      }
    }

    // add any supplied system properties
    String[] props = commandLine.getValues(SYSPROPS_OPTION);
    if (props != null && props.length > 0){
      for(String prop : props){
        String[] sysprop = StringUtils.split(prop, "=", 2);
        if (sysprop.length != 2){
          continue;
        }
        if (sysprop[0].startsWith("-D")){
          sysprop[0] = sysprop[0].substring(2);
        }
        Variable var = new Variable();
        var.setKey(sysprop[0]);
        var.setValue(sysprop[1]);
        java.addSysproperty(var);
      }
    }

    // add any env vars
    String[] envs = commandLine.getValues(ENVARGS_OPTION);
    if (envs != null && envs.length > 0){
      for(String env : envs){
        String[] envvar = StringUtils.split(env, "=", 2);
        if (envvar.length != 2){
          continue;
        }
        Variable var = new Variable();
        var.setKey(envvar[0]);
        var.setValue(envvar[1]);
        java.addEnv(var);
      }
    }

    // add any supplied command line args
    String[] args = commandLine.getValues(Options.ARGS_OPTION);
    if (args != null && args.length > 0){
      for(String arg : args){
        Argument a = java.createArg();
        a.setValue(arg);
      }
    }

    java.execute();

    return null;
  }
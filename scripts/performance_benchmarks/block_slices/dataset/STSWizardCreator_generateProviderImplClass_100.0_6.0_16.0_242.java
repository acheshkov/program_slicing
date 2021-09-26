public void generateProviderImplClass(Project project, FileObject targetFolder,
            final String targetName, final WsdlService service, final WsdlPort port, 
            URL wsdlURL) throws Exception 
    {
        initProjectInfo(project);
        
        String serviceID = service.getName();
        
        final JAXWSSupport jaxWsSupport = JAXWSSupport.getJAXWSSupport(project.getProjectDirectory());
            
        FileObject implClassFo = GenerationUtils.createClass(targetFolder, targetName, null);
        ClassPath classPath = ClassPath.getClassPath(implClassFo, ClassPath.SOURCE);            
        String serviceImplPath = classPath.getResourceName(implClassFo, '.', false);
        String portJavaName = port.getJavaName();
        String artifactsPckg = portJavaName.substring(0, portJavaName.lastIndexOf('.'));

        serviceID = jaxWsSupport.addService(targetName, serviceImplPath, 
                wsdlURL.toString(), service.getName(), port.getName(), artifactsPckg, 
                jsr109Supported && Util.isJavaEE5orHigher(project), true);
        final String wsdlLocation = jaxWsSupport.getWsdlLocation(serviceID);
                       
        final String[] fqn = new String[1];
        JavaSource targetSource = JavaSource.forFileObject(implClassFo);
        CancellableTask<WorkingCopy> task = new CancellableTask<WorkingCopy>() {

            @Override
            public void run(WorkingCopy workingCopy) throws java.io.IOException {
                workingCopy.toPhase(Phase.RESOLVED);
                GenerationUtils genUtils = GenerationUtils.newInstance(workingCopy);
                if (genUtils!=null) {     
                    TreeMaker make = workingCopy.getTreeMaker();
                    ClassTree javaClass = genUtils.getClassTree();
                    Element element = workingCopy.getTrees().getElement( 
                            workingCopy.getTrees().getPath(
                                    workingCopy.getCompilationUnit(), javaClass));
                    if ( element instanceof TypeElement ){
                        fqn[0] = ((TypeElement)element).getQualifiedName().toString();
                    }
                    ClassTree modifiedClass;
                    
                    // not found on classpath, because the runtime jar is not on classpath by default
                    String baseStsImpl = "com.sun.xml.ws.security.trust.sts.BaseSTSImpl"; //NOI18N

                    // create parameters
                    List<AnnotationTree> annotations = new ArrayList<AnnotationTree>();
                    AnnotationTree resourceAnnotation = make.Annotation(
                        make.QualIdent("javax.annotation.Resource"), //NOI18N
                        Collections.<ExpressionTree>emptyList()
                    );
                    annotations.add(resourceAnnotation);
                    
                    List<VariableTree> classField = new ArrayList<VariableTree>();
                    // final ObjectOutput arg0
                    classField.add(make.Variable(
                            make.Modifiers(
                                Collections.<Modifier>emptySet(),
                                annotations
                            ),
                            "context", // name
                            make.QualIdent("javax.xml.ws.WebServiceContext"), //NOI18N parameter type
                            null // initializer - does not make sense in parameters.
                    ));
                    
                    modifiedClass = genUtils.addClassFields(javaClass, classField);
                    
                    ParameterizedTypeTree t = make.ParameterizedType(
                            make.QualIdent("javax.xml.ws.Provider"), //NOI18N
                            Collections.singletonList(
                                    make.QualIdent("javax.xml.transform.Source"))); //NOI18N
                    modifiedClass = make.addClassImplementsClause(modifiedClass, t);
                    modifiedClass = make.setExtends(modifiedClass, make.Identifier(baseStsImpl));
                    
                    //add @WebServiceProvider annotation
                    List<ExpressionTree> attrs = new ArrayList<ExpressionTree>();
                    attrs.add(
                        make.Assignment(make.Identifier("serviceName"), make.Literal(service.getName()))); //NOI18N
                    attrs.add(
                        make.Assignment(make.Identifier("portName"), make.Literal(port.getName()))); //NOI18N
                    attrs.add(
                        make.Assignment(make.Identifier("targetNamespace"), make.Literal(port.getNamespaceURI()))); //NOI18N
                    attrs.add(
                        make.Assignment(make.Identifier("wsdlLocation"), make.Literal(wsdlLocation))); //NOI18N
                    AnnotationTree WSAnnotation = make.Annotation(
                        make.QualIdent("javax.xml.ws.WebServiceProvider"), //NOI18N
                        attrs
                    );
                    modifiedClass = genUtils.addAnnotation(modifiedClass, WSAnnotation);
                                        
                    //add @WebServiceProvider annotation
                    TypeElement modeAn = workingCopy.getElements().getTypeElement("javax.xml.ws.ServiceMode"); //NOI18N
                    List<ExpressionTree> attrsM = new ArrayList<ExpressionTree>();

                    ExpressionTree mstree = make.MemberSelect(
                            make.QualIdent("javax.xml.ws.Service.Mode"), "PAYLOAD");    // NOI18N
                    
                    attrsM.add(
                        make.Assignment(make.Identifier("value"), mstree)); //NOI18N
                    AnnotationTree modeAnnot = make.Annotation(
                        make.QualIdent(modeAn), 
                        attrsM
                    );
                    modifiedClass = genUtils.addAnnotation(modifiedClass, modeAnnot);

                    // add @Stateless annotation
                    if (projectType == EJB_PROJECT_TYPE) {//EJB project
                        AnnotationTree statelessAnnotation = make.Annotation(
                                make.QualIdent("javax.ejb.Stateless"),  // NOI18N
                            Collections.<ExpressionTree>emptyList()
                        );
                        modifiedClass = genUtils.addAnnotation(modifiedClass, 
                                statelessAnnotation);
                    }

                    // create parameters
                    List<VariableTree> params = new ArrayList<VariableTree>();
                    // final ObjectOutput arg0
                    params.add(make.Variable(
                            make.Modifiers(
                                Collections.<Modifier>emptySet(),
                                Collections.<AnnotationTree>emptyList()
                            ),
                            "rstElement", // name
                            make.QualIdent("javax.xml.transform.Source"), //NOI18N parameter type
                            null // initializer - does not make sense in parameters.
                    ));

                    // create method
                    ModifiersTree methodModifiers = make.Modifiers(
                        Collections.<Modifier>singleton(Modifier.PUBLIC),
                        Collections.<AnnotationTree>emptyList()
                    );
                    
                    List<ExpressionTree> exc = new ArrayList<ExpressionTree>();
                    
                    MethodTree method = make.Method(
                            methodModifiers, // public
                            "invoke", // operation name
                            make.QualIdent("javax.xml.transform.Source"), //NOI18N return type 
                            Collections.<TypeParameterTree>emptyList(), // type parameters - none
                            params,
                            exc, // throws 
                            "{ return super.invoke(rstElement); }", // body text
                            null // default value - not applicable here, used by annotations
                    );
                    modifiedClass =  make.addClassMember(modifiedClass, method); 
                    
                    // create method
                    ModifiersTree msgContextModifiers = make.Modifiers(
                        Collections.<Modifier>singleton(Modifier.PROTECTED),
                        Collections.<AnnotationTree>emptyList()
                    );
                    
                    List<ExpressionTree> excMsg = new ArrayList<ExpressionTree>();
                    
                    MethodTree methodMsgContext = make.Method(
                            msgContextModifiers, // public
                            "getMessageContext", // operation name
                            make.QualIdent("javax.xml.ws.handler.MessageContext"), //NOI18N return type 
                            Collections.<TypeParameterTree>emptyList(), // type parameters - none
                            Collections.<VariableTree>emptyList(),
                            excMsg, // throws 
                            "{ MessageContext msgCtx = context.getMessageContext();\nreturn msgCtx; }", // body text
                            null // default value - not applicable here, used by annotations
                    );
                    modifiedClass =  make.addClassMember(modifiedClass, methodMsgContext);                     
                    
                    workingCopy.rewrite(javaClass, modifiedClass);
                }
            }

            @Override
            public void cancel() { 
            }
        };
        
        targetSource.runModificationTask(task).commit();

        String url = "/" + targetName + "Service";
        String mexUrl = url +"/mex";

        WsitProvider wsitProvider = project.getLookup().lookup(WsitProvider.class);
        if (wsitProvider != null) {
            wsitProvider.addServiceDDEntry(serviceImplPath, mexUrl, targetName);
        }

        FileObject ddFolder = jaxWsSupport.getDeploymentDescriptorFolder();
        FileObject sunjaxwsFile = ddFolder.getFileObject("sun-jaxws.xml");
        if(sunjaxwsFile == null){
            WSUtils.generateSunJaxwsFile(ddFolder);
            sunjaxwsFile = ddFolder.getFileObject("sun-jaxws.xml");
        }
        Endpoints endpoints = EndpointsProvider.getDefault().getEndpoints(sunjaxwsFile);
        Endpoint endpoint = endpoints.newEndpoint();
        endpoint.setEndpointName(Util.MEX_NAME);
        endpoint.setImplementation(Util.MEX_CLASS_NAME);
        endpoint.setUrlPattern(mexUrl);
        endpoints.addEnpoint(endpoint);
        
        if ( fqn[0]!= null ){
            endpoint = endpoints.newEndpoint();
            endpoint.setEndpointName(targetName);
            endpoint.setImplementation(fqn[0]);
            endpoint.setUrlPattern(url);
            endpoints.addEnpoint(endpoint);
        }
        
        FileLock lock = null;
        OutputStream os = null;
        synchronized (this) {
            try{
                lock = sunjaxwsFile.lock();
                os = sunjaxwsFile.getOutputStream(lock);
                endpoints.write(os);
            }finally{
                if(lock != null)
                    lock.releaseLock();

                if(os != null)
                    os.close();
            }
        }
        
        //open in the editor
        DataObject dobj = DataObject.find(implClassFo);
        implClassFo.setAttribute(STS_WEBSERVICE, Boolean.TRUE);
        implClassFo.addFileChangeListener( new FileChangeAdapter(){
           /* (non-Javadoc)
            * @see org.openide.filesystems.FileChangeAdapter#fileDeleted(org.openide.filesystems.FileEvent)
            */
            @Override
            public void fileDeleted( FileEvent fe ) {
                try {
                    jaxWsSupport.removeNonJsr109Entries(Util.MEX_NAME);
                    jaxWsSupport.removeNonJsr109Entries(fqn[0]);
                    jaxWsSupport.removeNonJsr109Entries(targetName);
                }
                catch(IOException e ){
                    logger.log( Level.WARNING, null , e);
                }
            } 
        });
        openFileInEditor(dobj);
    }
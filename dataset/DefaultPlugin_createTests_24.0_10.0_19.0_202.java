@Override
    protected FileObject[] createTests(
                                final FileObject[] filesToTest,
                                final FileObject targetRoot,
                                final Map<CreateTestParam, Object> params) {
        //XXX: not documented that in case that if filesToTest is <null>,
        //the target root param works as a target folder
        Project project = FileOwnerQuery.getOwner(targetRoot);
        if (project != null) {
            File projectFile = FileUtil.toFile(project.getProjectDirectory());
            if (projectFile != null) {
                logJUnitUsage(Utilities.toURI(projectFile));
            }
        }
        ProgressIndicator progress = new ProgressIndicator();
        progress.show();

        String msg = NbBundle.getMessage(
                    DefaultPlugin.class,
                    "MSG_StatusBar_CreateTest_Begin");                  //NOI18N
        progress.displayStatusText(msg);
        generatingIntegrationTest = Boolean.TRUE.equals(params.get(CreateTestParam.INC_GENERATE_INTEGRATION_TEST));

        final TestCreator testCreator = new TestCreator(params, junitVer);
        
        CreationResults results;
        try {
            final String templateId;
            final String suiteTemplateId;
            boolean forTestSuite
                    = (filesToTest != null)
                      && (filesToTest.length != 0)
                      && ((filesToTest.length > 1) || !filesToTest[0].isData());
            switch (junitVer) {
                case JUNIT3:
                    templateId = "PROP_junit3_testClassTemplate";       //NOI18N
                    suiteTemplateId = forTestSuite
                                      ? "PROP_junit3_testSuiteTemplate" //NOI18N
                                      : null;
                    break;
                case JUNIT4:
                    templateId = "PROP_junit4_testClassTemplate";       //NOI18N
                    suiteTemplateId = forTestSuite
                                      ? "PROP_junit4_testSuiteTemplate" //NOI18N
                                      : null;
                    break;
                case JUNIT5:
                    templateId = "PROP_junit5_testClassTemplate";       //NOI18N
                    suiteTemplateId = null;
                    break;
                default:
                    assert false;
                    templateId = null;
                    suiteTemplateId = null;
                    break;
            }
            DataObject doTestTempl = (templateId != null)
                                     ? loadTestTemplate(templateId)
                                     : null;
            if (doTestTempl == null) {
                return null;
            }
            DataObject doSuiteTempl = (suiteTemplateId != null)
                                      ? loadTestTemplate(suiteTemplateId)
                                      : null;
            if (forTestSuite && (doSuiteTempl == null)) {
                return null;
            }
            
            Map<String, Boolean> templateParams = createTemplateParams(params);
            setAnnotationsSupport(targetRoot, junitVer, templateParams);

            if ((filesToTest == null) || (filesToTest.length == 0)) {
                //XXX: Not documented that filesToTest may be <null>
                
                addTemplateParamEntry(params, CreateTestParam.INC_CODE_HINT,
                                      templateParams, templatePropMethodPH);

                String testClassName = (String) params.get(CreateTestParam.CLASS_NAME);
                assert testClassName != null;
                results = new CreationResults(1);
                DataObject testDataObj = createEmptyTest(targetRoot,
                                                         testClassName,
                                                         testCreator,
                                                         templateParams,
                                                         doTestTempl);
                if (testDataObj != null) {
                    results.addCreated(testDataObj);
                }
                
            } else {
                ClassPath testClassPath = ClassPathSupport.createClassPath(
                                                new FileObject[] {targetRoot});
                if (!forTestSuite) {
                    String testClassName = (String) params.get(CreateTestParam.CLASS_NAME);
                    if (testClassName == null) {
                        String srcClassName
                                = ClassPath.getClassPath(filesToTest[0], SOURCE)
                                  .getResourceName(filesToTest[0], '.', false);
                        if(generatingIntegrationTest) {
                            testClassName = getIntegrationTestClassName(srcClassName);
                        } else {
                            testClassName = getTestClassName(srcClassName);
                        }
                    }
                    try {
                        results = createSingleTest(
                                filesToTest[0],
                                testClassName,
                                testCreator,
                                templateParams,
                                doTestTempl,
                                testClassPath,
                                TestabilityResult.NO_TESTEABLE_METHODS.getReasonValue(),
                                null,              //parent suite
                                progress);
                    } catch (CreationError ex) {
                        ErrorManager.getDefault().notify(ex);
                        results = new CreationResults(1);
                    }
                } else {
                    results = new CreationResults();

                    // go through all nodes
                    for (FileObject fileToTest : filesToTest) {
                        try {
                            results.combine(createTests(fileToTest,
                                                        testCreator,
                                                        templateParams,
                                                        doTestTempl,
                                                        doSuiteTempl,
                                                        testClassPath,
                                                        null,
                                                        progress));
                        } catch (CreationError e) {
                            ErrorManager.getDefault().notify(e);
                        }
                    }
                }
            }
        } finally {
            progress.hide();
        }

        final Set<SkippedClass> skipped = results.getSkipped();
        final Set<DataObject> created = results.getCreated();
        if (!skipped.isEmpty() || created.isEmpty()) {
            // something was skipped
            String message = "";
            if (skipped.size() == 1) {
                // one class? report it
                SkippedClass skippedClass = skipped.iterator().next();

                message = NbBundle.getMessage(
                        DefaultPlugin.class,
                        "MSG_skipped_class",                            //NOI18N
                        skippedClass.clsName,
                        strReason(skippedClass.reason, "COMMA", "AND"));//NOI18N
            } else {
                // more classes, report a general error
                // combine the results
                TestabilityResult reason = TestabilityResult.OK;
                for (SkippedClass sc : skipped) {
                    reason = TestabilityResult.combine(reason, sc.reason);
                }

                message = NbBundle.getMessage(
                        DefaultPlugin.class,
                        "MSG_skipped_classes",                          //NOI18N
                        strReason(reason, "COMMA", "OR"));              //NOI18N
            }

            String noMessage = "";
            if (created.isEmpty()) {
                // nothing was created
                noMessage = NbBundle.getMessage(
                        DefaultPlugin.class,
                        "MSG_No_test_created");     //NOI18N
            }
            final String finalMessage = (message.isEmpty()) ? noMessage : message.concat("\n\n").concat(noMessage);     //NOI18N

            if (!finalMessage.isEmpty()) {
                Mutex.EVENT.writeAccess(new Runnable() {

                    public void run() {
                        JUnitTestUtil.notifyUser(finalMessage, NotifyDescriptor.INFORMATION_MESSAGE);
                    }
                });
            }
        }
        
        FileObject[] createdFiles;
        if (created.isEmpty()) {
            createdFiles = new FileObject[0];
        } else {
            createdFiles = new FileObject[created.size()];
            int i = 0;
            for (DataObject dObj : created) {
                createdFiles[i++] = dObj.getPrimaryFile();
            }
        }
        return createdFiles;
    }
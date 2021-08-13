    public static Collection<FileObject> createProjectFromTemplate(
                        final FileObject template, File projectLocation, 
                        final String name, final String serverID) throws IOException {
        assert template != null && projectLocation != null && name != null;
        ArrayList<FileObject> projects = new ArrayList<FileObject>();
        if (template.getExt().endsWith("zip")) {  //NOI18N
            FileObject prjLoc = createProjectFolder(projectLocation);
            InputStream is = template.getInputStream();
            try {
                unzip(is, prjLoc);
                projects.add(prjLoc);
                // update project.xml
                File projXml = FileUtil.toFile(prjLoc.getFileObject(AntProjectHelper.PROJECT_XML_PATH));
                Document doc = XMLUtil.parse(new InputSource(projXml.toURI().toString()), false, true, null, null);
                NodeList nlist = doc.getElementsByTagNameNS(PROJECT_CONFIGURATION_NAMESPACE, "name");       //NOI18N
                if (nlist != null) {
                    for (int i=0; i < nlist.getLength(); i++) {
                        Node n = nlist.item(i);
                        if (n.getNodeType() != Node.ELEMENT_NODE) {
                            continue;
                        }
                        Element e = (Element)n;
                        
                        replaceText(e, name);
                    }
                    saveXml(doc, prjLoc, AntProjectHelper.PROJECT_XML_PATH);
                }
            } catch (Exception e) {
                throw new IOException(e.toString());
            } finally {
                if (is != null) is.close();
            }
            prjLoc.refresh(false);
        } else {
            String files = (String) template.getAttribute("files");
            if ((files != null) && (files.length() > 0)) {
                StringTokenizer st = new StringTokenizer(files, ",");
                while (st.hasMoreElements()) {
                    String prjName = st.nextToken();
                    if ((prjName == null) || (prjName.trim().equals(""))) continue;
                    InputStream is = WebSampleProjectGenerator.class.getResourceAsStream(prjName);
                    try {
                        FileObject prjLoc = createProjectFolder(new File(projectLocation, prjName.substring(prjName.lastIndexOf("/")+1, prjName.indexOf('.'))));
                        unzip(is, prjLoc);
                        projects.add(prjLoc);
                        Boolean needsDefaults = (Boolean)template.getAttribute("needsdefaults");
                        if (needsDefaults) {
                            DevDefaultsProvider.getDefault().fillDefaultsToServer(serverID);
                        }
                    } catch (Exception e) {
                        Exceptions.printStackTrace(e);
                    } finally {
                        if (is != null) is.close();
                    }
                }
            }
        }
        return projects;
    }
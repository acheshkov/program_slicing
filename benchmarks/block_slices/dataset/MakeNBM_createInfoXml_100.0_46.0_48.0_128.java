private Document createInfoXml(final Attributes attr) throws BuildException {
        DOMImplementation domimpl;
        try {
            domimpl = DocumentBuilderFactory.newInstance().newDocumentBuilder().getDOMImplementation();
        } catch (ParserConfigurationException x) {
            throw new BuildException(x, getLocation());
        }
        String loc = attr.getValue("locale");
        if (loc == null) {
            throw new BuildException("Got module attributes for undefined locale", getLocation());
        } else {
            log("Creating info.xml from module attributes for locale '"+loc+"'", Project.MSG_VERBOSE);
        }
        
        String pub, sys;
        if (preferredupdate != null && !("".equals(preferredupdate))) {
            pub = "-//NetBeans//DTD Autoupdate Module Info 2.7//EN";
            sys = "http://www.netbeans.org/dtds/autoupdate-info-2_7.dtd";
        } else if (attr.getValue("AutoUpdate-Show-In-Client") != null || attr.getValue("AutoUpdate-Essential-Module") != null ||
                attr.getValue("OpenIDE-Module-Recommends") != null || attr.getValue("OpenIDE-Module-Needs") != null) {
            pub = "-//NetBeans//DTD Autoupdate Module Info 2.5//EN";
            sys = "http://www.netbeans.org/dtds/autoupdate-info-2_5.dtd";
        } else if (targetcluster != null && !("".equals(targetcluster))) {
            pub = "-//NetBeans//DTD Autoupdate Module Info 2.4//EN";
            sys = "http://www.netbeans.org/dtds/autoupdate-info-2_4.dtd";
        } else {
            // #74866: no need for targetcluster, so keep compat w/ 5.0 AU.
            pub = "-//NetBeans//DTD Autoupdate Module Info 2.3//EN";
            sys = "http://www.netbeans.org/dtds/autoupdate-info-2_3.dtd";
        }
        Document doc = domimpl.createDocument(null, "module", domimpl.createDocumentType("module", pub, sys));
        String codenamebase = attr.getValue("OpenIDE-Module");
        if (codenamebase == null) {
            Iterator<Object> it = attr.keySet().iterator();
            Name key; String val;
            while (it.hasNext()) {
                key = (Name) it.next();
                val = attr.getValue(key);
                log(key+" is '"+val+"'", Project.MSG_VERBOSE);
            }
            throw new BuildException("invalid manifest, does not contain OpenIDE-Module", getLocation());
        }
        // Strip major release number if any.
        int idx = codenamebase.lastIndexOf('/');
        if (idx != -1) codenamebase = codenamebase.substring(0, idx);
        Element module = doc.getDocumentElement();
        module.setAttribute("codenamebase", codenamebase);
        if (homepage != null) {
            module.setAttribute("homepage", homepage);
        }
        if (distribution != null) {
            module.setAttribute("distribution", distribution);
        } else {
            throw new BuildException("NBM distribution URL is not set", getLocation());
        }
        maybeAddLicenseName(module);
        module.setAttribute("downloadsize", "0");
        if (needsrestart != null) {
            module.setAttribute("needsrestart", needsrestart);
        }
        if (global != null && !("".equals(global))) {
            module.setAttribute("global", global);
        }
        if (preferredupdate != null && !("".equals(preferredupdate))) {
            module.setAttribute("preferredupdate", preferredupdate);
        }
        if (targetcluster != null && !("".equals(targetcluster))) {
            module.setAttribute("targetcluster", targetcluster);
        }
        if (moduleauthor != null) {
            module.setAttribute("moduleauthor", moduleauthor);
        }
        if (releasedate == null || "".equals(releasedate)) {
            // if date is null, set today
            releasedate = DATE_FORMAT.format(new Date(System.currentTimeMillis()));
        }
        module.setAttribute("releasedate", releasedate);
        if (desc != null) {
            module.appendChild(doc.createElement("description")).appendChild(desc.getTextNode(doc));
        }
        if (notification != null) {
            module.appendChild(doc.createElement("module_notification")).appendChild(notification.getTextNode(doc));
        }
        if (externalPackages != null) {
            Iterator<ExternalPackage> exp = externalPackages.iterator();
            while (exp.hasNext()) {
                ExternalPackage externalPackage = exp.next();
                if (externalPackage.name == null ||
                        externalPackage.targetName == null ||
                        externalPackage.startUrl == null)
                    throw new BuildException("Must define name, targetname, starturl for external package");
                Element el = doc.createElement("external_package");
                el.setAttribute("name", externalPackage.name);
                el.setAttribute("target_name", externalPackage.targetName);
                el.setAttribute("start_url", externalPackage.startUrl);
                if (externalPackage.description != null) {
                    el.setAttribute("description", externalPackage.description);
                }
                module.appendChild(el);
            }
        }
        // Write manifest attributes.
        Element el = doc.createElement("manifest");
        List<String> attrNames = new ArrayList<>(attr.size());
        for(Object key: attr.keySet()) {
            attrNames.add(((Attributes.Name)key).toString());
        }
        Collections.sort(attrNames);
        for(String name: attrNames) {
            if (name.matches("OpenIDE-Module(|-(Name|(Specification|Implementation)-Version|(Module|Package|Java|IDE)-Dependencies|" +
                    "(Short|Long)-Description|Display-Category|Provides|Requires|Recommends|Needs|Fragment-Host))|AutoUpdate-(Show-In-Client|Essential-Module)")) {
                el.setAttribute(name, attr.getValue(name));
            }
        }
        module.appendChild(el);
        maybeAddLicense(module);
        if (updaterJar != null && updaterJar.size() > 0) {
            try {
                ByteArrayOutputStream baos = new ByteArrayOutputStream();
                XMLUtil.write(doc, baos);
                validateAgainstAUDTDs(new InputSource(new ByteArrayInputStream(baos.toByteArray())), updaterJar, this);
            } catch (Exception x) {
                throw new BuildException("Could not validate Info.xml before writing: " + x, x, getLocation());
            }
        } else {
            log("No updater.jar specified, cannot validate Info.xml against DTD", Project.MSG_WARN);
        }
        return doc;
    }
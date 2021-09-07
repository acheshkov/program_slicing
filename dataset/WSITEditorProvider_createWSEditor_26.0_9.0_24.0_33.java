public WSEditor createWSEditor(Lookup nodeLookup) {
        FileObject srcRoot = nodeLookup.lookup(FileObject.class);
        if (srcRoot != null) {
            Project prj = FileOwnerQuery.getOwner(srcRoot);
            JaxWsModel jaxWsModel = prj.getLookup().lookup(JaxWsModel.class);
            if (jaxWsModel != null) {
                return new WSITEditor(jaxWsModel);
            } else {
                JaxWsService service = nodeLookup.lookup(JaxWsService.class);
                if (service != null) {
                    JAXWSLightSupport jaxWsSupport = nodeLookup.lookup(JAXWSLightSupport.class);
                    if (jaxWsSupport != null) {
                        return new MavenWSITEditor(jaxWsSupport, service, prj);
                    } else {
                        jaxWsSupport = JAXWSLightSupport.getJAXWSLightSupport(srcRoot);
                        if (jaxWsSupport != null) {
                            return new MavenWSITEditor(jaxWsSupport, service, prj);
                        }
                    }
                }
            }
        } else {
            JaxWsService service = nodeLookup.lookup(JaxWsService.class);
            JAXWSLightSupport jaxWsSupport = nodeLookup.lookup(JAXWSLightSupport.class);
            if ((service != null) && (jaxWsSupport != null)) {
                FileObject wsdlFolder = jaxWsSupport.getWsdlFolder(false);
                if (wsdlFolder != null) {
                    Project prj = FileOwnerQuery.getOwner(wsdlFolder);
                    return new MavenWSITEditor(jaxWsSupport, service, prj);
                }
            }
        }
        return null;
    }
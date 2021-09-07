protected ASDDVersion getTargetAppServerVersion() {
        ASDDVersion result = null;
        J2eeModuleProvider provider = getProvider(primarySunDD.getParentFile());
        if (null == provider) {
            return result;
        }
        String serverType = Utils.getInstanceReleaseID(provider); // provider.getServerInstanceID();
// [/tools/as81ur2]deployer:Sun:AppServer::localhost:4848, serverType: J2EE
// [/tools/as82]deployer:Sun:AppServer::localhost:4848, serverType: J2EE
// [/tools/glassfish_b35]deployer:Sun:AppServer::localhost:4948, serverType: J2EE
        if (Arrays.asList(sunServerIds).contains(serverType)) {
            // NOI18N
            String instance = provider.getServerInstanceID();
            if (Utils.notEmpty(instance)) {
                try {
                    String asInstallPath = instance.substring(1, instance.indexOf("]deployer:"));
                    if (asInstallPath.contains(File.pathSeparator)) 
                        asInstallPath = asInstallPath.substring(0, asInstallPath.indexOf(File.pathSeparator));
                    File asInstallFolder = new File(asInstallPath);
                    if (asInstallFolder.exists()) {
                        result = getInstalledAppServerVersion(asInstallFolder);
                    }
                } catch (IndexOutOfBoundsException ex) {
                    // Can't identify server install folder.
                    LOGGER.log(Level.WARNING, NbBundle.getMessage(
                            GlassfishConfiguration.class, "ERR_NoServerInstallLocation", instance)); // NOI18N
                } catch (NullPointerException ex) {
                    LOGGER.log(Level.INFO, ex.getLocalizedMessage(), ex);
                }
            }
        } else if ("SUNWebserver7".equals(serverType)) {
            // NOI18N
            result = ASDDVersion.SUN_APPSERVER_8_1;
        }

        return result;
    }
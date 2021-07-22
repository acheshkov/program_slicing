    private void loadManifest() throws IOException {
        Util.err.fine("loading manifest of " + jar);
        File jarBeingOpened = null; // for annotation purposes
        try {
            if (reloadable) {
                // Never try to cache reloadable JARs.
                jarBeingOpened = physicalJar; // might be null
                ensurePhysicalJar();
                jarBeingOpened = physicalJar; // might have changed
                JarFile jarFile = new JarFile(physicalJar, false);
                try {
                    Manifest m = jarFile.getManifest();
                    if (m == null) throw new IOException("No manifest found in " + physicalJar); // NOI18N
                    manifest = m;
                } finally {
                    jarFile.close();
                }
            } else {
                jarBeingOpened = jar;
                manifest = getManager().loadManifest(jar);
            }
        } catch (IOException e) {
            if (jarBeingOpened != null) {
                Exceptions.attachMessage(e,
                                         "While loading manifest from: " +
                                         jarBeingOpened); // NOI18N
            }
            throw e;
        }
    }
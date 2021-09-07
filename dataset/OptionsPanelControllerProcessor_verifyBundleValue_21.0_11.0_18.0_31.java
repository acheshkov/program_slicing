private String verifyBundleValue(String bundle, String key, boolean samePackage, Annotation annotation, String annotationMethod) throws LayerGenerationException {
        if (processingEnv == null) {
            return "";
        }
        if (samePackage) {
            for (Element e = originatingElement; e != null; e = e.getEnclosingElement()) {
                NbBundle.Messages m = e.getAnnotation(NbBundle.Messages.class);
                if (m != null) {
                    for (String kv : m.value()) {
                        if (kv.startsWith(key + "=")) {
                            return bundle.concat("#").concat(key);
                        }
                    }
                }
            }
        }
        try {
            InputStream is = layer(originatingElement).validateResource(bundle.replace('.', '/') + ".properties", originatingElement, null, null, false).openInputStream();
            try {
                Properties p = new Properties();
                p.load(is);
                if (p.getProperty(key) == null) {
                    throw new LayerGenerationException("No key '" + key + "' found in " + bundle, originatingElement, processingEnv, annotation, annotationMethod);
                }
                return bundle.concat("#").concat(key);
            } finally {
                is.close();
            }
        } catch (IOException x) {
            throw new LayerGenerationException("Could not open " + bundle + ": " + x, originatingElement, processingEnv, annotation, annotationMethod);
        }
    }
@Override public boolean process(Set<? extends TypeElement> annotations, RoundEnvironment roundEnv) {
        if (!roundEnv.processingOver()) {
            for (Element e : roundEnv.getElementsAnnotatedWith(StaticResource.class)) {
                StaticResource sr = e.getAnnotation(StaticResource.class);
                if (sr == null) {
                    continue;
                }
                Object v = ((VariableElement) e).getConstantValue();
                if (!(v instanceof String)) {
                    processingEnv.getMessager().printMessage(Diagnostic.Kind.ERROR, "@StaticResource may only be used on a String constant", e);
                    continue;
                }
                String resource = (String) v;
                // remainder adapted from LayerBuilder, but cannot reference that here
                if (sr.relative()) {
                    try {
                        resource = new URI(null, findPackage(e).replace('.', '/') + "/", null).resolve(new URI(null, resource, null)).getPath();
                    } catch (URISyntaxException x) {
                        processingEnv.getMessager().printMessage(Diagnostic.Kind.ERROR, x.getMessage(), e);
                        continue;
                    }
                }
                if (resource.startsWith("/")) {
                    processingEnv.getMessager().printMessage(Diagnostic.Kind.ERROR, "do not use leading slashes on resource paths", e);
                    continue;
                }
                if (sr.searchClasspath()) {
                    boolean ok = false;
                    for (JavaFileManager.Location loc : new JavaFileManager.Location[] {StandardLocation.SOURCE_PATH, /* #181355 */ StandardLocation.CLASS_OUTPUT, StandardLocation.CLASS_PATH, StandardLocation.PLATFORM_CLASS_PATH}) {
                        try {
                            processingEnv.getFiler().getResource(loc, "", resource).openInputStream().close();
                            ok = true;
                        } catch (IOException ex) {
                            continue;
                        }
                    }
                    if (!ok) {
                        processingEnv.getMessager().printMessage(Diagnostic.Kind.ERROR, "cannot find resource " + resource, e);
                    }
                } else {
                    try {
                        try {
                            processingEnv.getFiler().getResource(StandardLocation.SOURCE_PATH, "", resource).openInputStream().close();
                        } catch (FileNotFoundException x) {
                            processingEnv.getFiler().getResource(StandardLocation.CLASS_OUTPUT, "", resource).openInputStream().close();
                        }
                    } catch (IOException x) {
                        processingEnv.getMessager().printMessage(Diagnostic.Kind.ERROR, "cannot find resource " + resource, e);
                    }
                }
            }
        }
        return true;
    }
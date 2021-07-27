    private boolean isClassOf(Element e, Class providerClass) {
        switch (e.getKind()) {
            case CLASS: {
                TypeElement te = (TypeElement) e;
                TypeMirror superType = te.getSuperclass();
                if (superType.getKind().equals(TypeKind.NONE)) {
                    return false;
                } else {
                    e = ((DeclaredType) superType).asElement();
                    String clazz = processingEnv.getElementUtils().getBinaryName((TypeElement) e).toString();
                    if (clazz.equals(providerClass.getName())) {
                        return true;
                    } else {
                        return isClassOf(e, providerClass);
                    }
                }
            }
            case METHOD: {
                TypeMirror retType = ((ExecutableElement) e).getReturnType();
                if (retType.getKind().equals(TypeKind.NONE)) {
                    return false;
                } else {
                    e = ((DeclaredType) retType).asElement();
                    String clazz = processingEnv.getElementUtils().getBinaryName((TypeElement) e).toString();
                    if (clazz.equals(providerClass.getName())) {
                        return true;
                    } else {
                        return isClassOf(e, providerClass);
                    }
                }
            }
            default:
                throw new IllegalArgumentException("Annotated element is not loadable as an instance: " + e);
        }
    }
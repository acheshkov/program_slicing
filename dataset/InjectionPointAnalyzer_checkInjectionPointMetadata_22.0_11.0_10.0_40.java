private void checkInjectionPointMetadata( VariableElement element,
            TypeMirror elementType , TypeElement parent, WebBeansModel model,
            AtomicBoolean cancel , Result result )
    {
        TypeElement injectionPointType = model.getCompilationController().
            getElements().getTypeElement(AnnotationUtil.INJECTION_POINT);
        if ( injectionPointType == null ){
            return;
        }
        Element varElement = model.getCompilationController().getTypes().asElement( 
                elementType );
        if ( !injectionPointType.equals(varElement)){
            return;
        }
        if ( cancel.get()){
            return;
        }
        List<AnnotationMirror> qualifiers = model.getQualifiers(element, true);
        AnnotationHelper helper = new AnnotationHelper(model.getCompilationController());
        Map<String, ? extends AnnotationMirror> qualifiersFqns = helper.
            getAnnotationsByType(qualifiers);
        boolean hasDefault = model.hasImplicitDefaultQualifier( element );
        if ( !hasDefault && qualifiersFqns.keySet().contains(AnnotationUtil.DEFAULT_FQN)){
            hasDefault = true;
        }
        if ( !hasDefault || cancel.get() ){
            return;
        }
        try {
            String scope = model.getScope( parent );
            if ( scope != null && !AnnotationUtil.DEPENDENT.equals( scope )){
                result.addError(element , model,  
                        NbBundle.getMessage(
                        InjectionPointAnalyzer.class, "ERR_WrongQualifierInjectionPointMeta"));            // NOI18N
            }
        }
        catch (CdiException e) {
            // this exception will be handled in the appropriate scope analyzer
            return;
        }
    }
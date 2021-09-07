public ClassTree generate() {
        
        ClassTree modifiedClazz = getClassTree();
        FileObject fo = FileUtil.toFileObject(new File(getWorkingCopy().getCompilationUnit().getSourceFile().toUri().getPath()));

        Project project = FileOwnerQuery.getOwner(fo);
        JPATargetInfo ti = project != null ? project.getLookup().lookup(JPATargetInfo.class) : null;
        boolean isEJB = false;
        if(ti != null){
            JPATargetInfo.TargetType tt = ti.getType(fo, getClassElement().getQualifiedName().toString());
            isEJB = JPATargetInfo.TargetType.EJB.equals(tt);
        }
        
        FieldInfo em = getEntityManagerFieldInfo();
        
        if(!em.isExisting()){
            List<ExpressionTree> attribs = new ArrayList<ExpressionTree>();
            attribs.add(getGenUtils().createAnnotationArgument("name", "persistence/LogicalName")); //NOI18N
            attribs.add(getGenUtils().createAnnotationArgument("unitName", getPersistenceUnitName())); //NOI18N
            modifiedClazz = getGenUtils().addAnnotation(modifiedClazz, getGenUtils().createAnnotation(PERSISTENCE_CONTEXT_FQN, attribs));
        }

        boolean simple = GenerationOptions.Operation.GET_EM.equals(getGenerationOptions().getOperation());//if simple (or with return etc) - no transactions
        if(!(isEJB || simple)){
            modifiedClazz = getTreeMaker().insertClassMember(modifiedClazz, getIndexForField(modifiedClazz), createUserTransaction());
        }
        
        ModifiersTree methodModifiers = getTreeMaker().Modifiers(
                Collections.<Modifier>singleton(Modifier.PROTECTED),
                Collections.<AnnotationTree>emptyList()
                );
        MethodTree newMethod = getTreeMaker().Method(
                methodModifiers,
                computeMethodName(),
                getTreeMaker().PrimitiveType(TypeKind.VOID),
                Collections.<TypeParameterTree>emptyList(),
                getParameterList(),
                Collections.<ExpressionTree>emptyList(),
                "{ " + getMethodBody(em, isEJB) + "}",
                null
                );
        
        return getTreeMaker().addClassMember(modifiedClazz, importFQNs(newMethod));
    }
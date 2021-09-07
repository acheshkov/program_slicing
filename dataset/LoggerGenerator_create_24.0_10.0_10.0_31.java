@Override
        public List<? extends CodeGenerator> create(Lookup context) {
            ArrayList<CodeGenerator> ret = new ArrayList<>();
            JTextComponent component = context.lookup(JTextComponent.class);
            CompilationController controller = context.lookup(CompilationController.class);
            if (component == null || controller == null) {
                return ret;
            }
            TreePath path = context.lookup(TreePath.class);
            path = controller.getTreeUtilities().getPathElementOfKind(TreeUtilities.CLASS_TREE_KINDS, path);
            if (path == null) {
                return ret;
            }
            try {
                controller.toPhase(JavaSource.Phase.ELEMENTS_RESOLVED);
            } catch (IOException ioe) {
                return ret;
            }
            TypeElement typeElement = (TypeElement) controller.getTrees().getElement(path);
            if (typeElement == null || !typeElement.getKind().isClass()) {
                return ret;
            }
            for (VariableElement ve : ElementFilter.fieldsIn(typeElement.getEnclosedElements())) {
                TypeMirror type = ve.asType();
                if (type.getKind() == TypeKind.DECLARED && ((TypeElement)((DeclaredType)type).asElement()).getQualifiedName().contentEquals(Logger.class.getName())) {
                    return ret;
                }
            }
            List<ElementNode.Description> descriptions = new ArrayList<>();
            ret.add(new LoggerGenerator(component, ElementNode.Description.create(controller, typeElement, descriptions, false, false)));
            return ret;
        }
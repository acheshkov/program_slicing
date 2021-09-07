public final Problem prepare(RefactoringElementsBag refactoringElements) {
        
        Problem problem = null;
        Problem current = null;
        for (RenameItem item : getRenameItems()){
            
            String newName = item.getNewFqn();
            String oldFqn = item.getOldFqn();
            
            /*
             * Additional fix for IZ#153294 - Error message when renaming a package that contains a dash character
             */
            if ( item.getProblem()!= null) {
                if ( problem == null ){
                    problem = item.getProblem();
                    current = problem;
                }
                else {
                    current.setNext( item.getProblem());
                    current = item.getProblem();
                }
                continue;
            }
            
            
            for (Servlet servlet : getServlets(oldFqn)){
                refactoringElements.add(getRefactoring(), new ServletRenameElement(newName, oldFqn, getWebModel(), webDD, servlet));
            }
            
            for (Listener listener : getListeners(oldFqn)){
                refactoringElements.add(getRefactoring(), new ListenerRenameElement(newName, oldFqn,  getWebModel(), webDD, listener));
            }
            
            for (Filter filter : getFilters(oldFqn)){
                refactoringElements.add(getRefactoring(), new FilterRenameElement(newName, oldFqn, getWebModel(), webDD, filter));
            }
            
            for (EjbRef ejbRef : getEjbRefs(oldFqn, true)){
                refactoringElements.add(getRefactoring(), new EjbRemoteRefRenameElement(newName, oldFqn, getWebModel(), webDD, ejbRef));
            }
            
            for (EjbRef ejbRef : getEjbRefs(oldFqn, false)){
                refactoringElements.add(getRefactoring(), new EjbHomeRefRenameElement(newName, oldFqn, getWebModel(), webDD, ejbRef));
            }
            
            for (EjbLocalRef ejbLocalRef : getEjbLocalRefs(oldFqn, false)){
                refactoringElements.add(getRefactoring(), new EjbLocalRefRenameElement(newName, oldFqn, getWebModel(), webDD, ejbLocalRef));
            }
            
            for (EjbLocalRef ejbLocalRef : getEjbLocalRefs(oldFqn, true)){
                refactoringElements.add(getRefactoring(), new EjbLocalHomeRefRenameElement(newName, oldFqn, getWebModel(), webDD, ejbLocalRef));
            }
        }
        
        return problem;
    }
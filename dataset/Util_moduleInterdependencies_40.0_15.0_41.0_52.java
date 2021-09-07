static Set<Module> moduleInterdependencies(Module m, boolean reverse, boolean transitive, boolean considerNeeds,
                                       Set<Module> modules, Map<String,Module> modulesByName, Map<String,Set<Module>> providersOf) {
        // XXX these algorithms could surely be made faster using standard techniques
        // for now the speed is not critical however
        if (reverse) {
            Set<Module> s = new HashSet<Module>();
            for (Module m2: modules) {
                if (m2 == m) {
                    continue;
                }
                if (moduleInterdependencies(m2, false, transitive, considerNeeds, modules, modulesByName, providersOf).contains(m)) {
                    s.add(m2);
                }
            }
            return s;
        } else {
            Set<Module> s = new HashSet<Module>();
            for (Dependency dep : m.getDependenciesArray()) {
                boolean needsProvider = dep.getType() == Dependency.TYPE_REQUIRES || 
                    considerNeeds && dep.getType() == Dependency.TYPE_NEEDS;
                if (m instanceof NetigsoModule && dep.getType() == Dependency.TYPE_RECOMMENDS) {
                    needsProvider = true;
                }
                if (needsProvider) {
                    Set<Module> providers = providersOf.get(dep.getName());
                    if (providers != null) {
                        s.addAll(providers);
                    }
                } else if (dep.getType() == Dependency.TYPE_MODULE) {
                    String cnb = (String)parseCodeName(dep.getName())[0];
                    Module m2 = modulesByName.get(cnb);
                    if (m2 != null) {
                        s.add(m2);
                    }
                }
            }
            s.remove(m);
            if (transitive) {
                Set<Module> toAdd;
                do {
                    toAdd = new HashSet<Module>();
                    for (Module m2: s) {
                        Set<Module> s2 = moduleInterdependencies(m2, false, false, considerNeeds, modules, modulesByName, providersOf);
                        s2.remove(m);
                        s2.removeAll(s);
                        toAdd.addAll(s2);
                    }
                    s.addAll(toAdd);
                } while (!toAdd.isEmpty());
            }
            return s;
        }
    }
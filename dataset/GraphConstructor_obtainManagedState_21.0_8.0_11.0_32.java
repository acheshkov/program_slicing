private int obtainManagedState(MavenDependencyNode dependencyNode) {        
        if (proj == null) {
            return GraphNode.UNMANAGED;
        }

        DependencyManagement dm = proj.getDependencyManagement();
        if (dm == null) {
            return GraphNode.UNMANAGED;
        }

        @SuppressWarnings("unchecked")
        List<Dependency> deps = dm.getDependencies();
        if (deps == null) {
            return GraphNode.UNMANAGED;
        }

        Artifact artifact = dependencyNode.getArtifact();
        String id = artifact.getArtifactId();
        String groupId = artifact.getGroupId();
        String version = artifact.getVersion();

        for (Dependency dep : deps) {
            if (id.equals(dep.getArtifactId()) && groupId.equals(dep.getGroupId())) {
                if (!version.equals(dep.getVersion())) {
                    return GraphNode.OVERRIDES_MANAGED;
                } else {
                    return GraphNode.MANAGED;
                }
            }
        }

        return GraphNode.UNMANAGED;
    }
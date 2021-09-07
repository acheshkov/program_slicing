String getTargetPackageName(FileObject fo) {
        if (isRenameRefactoring) {
            if (refactoring.getRefactoringSource().lookup(NonRecursiveFolder.class) !=null) {
                return getNewPackageName();
            }
            else {
                //folder rename
                FileObject folder = refactoring.getRefactoringSource().lookup(FileObject.class);
                ClassPath cp = ClassPath.getClassPath(folder, ClassPath.SOURCE);
                FileObject root = cp.findOwnerRoot(folder);
                String relativePath = FileUtil.getRelativePath(root, folder.getParent());
                String prefix = relativePath == null? "" : relativePath.replace('/','.');
                String relativePath1 = FileUtil.getRelativePath(folder, fo.isFolder() ? fo : fo.getParent());
                String postfix = relativePath1 == null? "" : relativePath1.replace('/', '.');
                String t = concat(prefix, getNewPackageName(), postfix);
                return t;
            }
        } else if (packagePostfix != null) {
            if (fo == null) {
                return getNewPackageName();
            }
            String postfix = (String) packagePostfix.get(fo);
            String packageName = concat(null, getNewPackageName(), postfix);
            return packageName;
        } else {
            return getNewPackageName();
        }
    }
public ICompilationUnit handleClosed(DidCloseTextDocumentParams params) {
		String uri = params.getTextDocument().getUri();
		ICompilationUnit unit = JDTUtils.resolveCompilationUnit(uri);
		if (unit == null) {
			return unit;
		}
		try {
			synchronized (toReconcile) {
				toReconcile.remove(unit);
			}
			if (isSyntaxMode(unit) || unit.getResource().isDerived()) {
				createDiagnosticsHandler(unit).clearDiagnostics();
			} else if (hasUnsavedChanges(unit)) {
				unit.discardWorkingCopy();
				unit.becomeWorkingCopy(new NullProgressMonitor());
				publishDiagnostics(unit, new NullProgressMonitor());
			}
			if (unit.equals(sharedASTProvider.getActiveJavaElement())) {
				sharedASTProvider.disposeAST();
			}
			unit.discardWorkingCopy();
			if (JDTUtils.isDefaultProject(unit)) {
				File f = new File(unit.getUnderlyingResource().getLocationURI());
				if (!f.exists()) {
					unit.delete(true, null);
				}
			}
		} catch (CoreException e) {
			JavaLanguageServerPlugin.logException("Error while handling document close. URI: " + uri, e);
		}

		return unit;
	}
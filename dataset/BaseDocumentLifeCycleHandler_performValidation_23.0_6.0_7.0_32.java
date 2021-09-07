private IStatus performValidation(IProgressMonitor monitor) throws JavaModelException {
		long start = System.currentTimeMillis();

		List<ICompilationUnit> cusToReconcile = new ArrayList<>();
		synchronized (toReconcile) {
			cusToReconcile.addAll(toReconcile);
			toReconcile.clear();
		}
		if (cusToReconcile.isEmpty()) {
			return Status.OK_STATUS;
		}
		// first reconcile all units with content changes
		SubMonitor progress = SubMonitor.convert(monitor, cusToReconcile.size() + 1);
		for (ICompilationUnit cu : cusToReconcile) {
			cu.reconcile(ICompilationUnit.NO_AST, true, null, progress.newChild(1));
		}
		JavaLanguageServerPlugin.logInfo("Reconciled " + toReconcile.size() + ". Took " + (System.currentTimeMillis() - start) + " ms");
		if (monitor.isCanceled()) {
			return Status.CANCEL_STATUS;
		}
		if (publishDiagnosticsJob != null) {
			publishDiagnosticsJob.cancel();
			try {
				publishDiagnosticsJob.join();
			} catch (InterruptedException e) {
				// ignore
			}
			publishDiagnosticsJob.schedule(400);
		} else {
			return publishDiagnostics(new NullProgressMonitor());
		}
		return Status.OK_STATUS;
	}
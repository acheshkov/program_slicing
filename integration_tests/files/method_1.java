	private Object safeCreateGui(MUIElement element) {
		// Obtain the necessary parent widget
		Object parent = null;
		MUIElement parentME = element.getParent();
		if (parentME == null)
			parentME = (MUIElement) ((EObject) element).eContainer();
		if (parentME != null) {
			AbstractPartRenderer renderer = getRendererFor(parentME);
			if (renderer != null) {
				if (!element.isVisible()) {
					parent = getLimboShell();
				} else {
					parent = renderer.getUIContainer(element);
				}
			}
		}

		// Obtain the necessary parent context
		IEclipseContext parentContext = null;
		if (element.getCurSharedRef() != null) {
			MPlaceholder ph = element.getCurSharedRef();
			parentContext = getContext(ph.getParent());
		} else if (parentContext == null && element.getParent() != null) {
			parentContext = getContext(element.getParent());
		} else if (parentContext == null && element.getParent() == null) {
			parentContext = getContext((MUIElement) ((EObject) element)
					.eContainer());
		}

		return safeCreateGui(element, parent, parentContext);
	}
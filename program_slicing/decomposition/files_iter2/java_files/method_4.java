		private void initializeImage() {
			// http://bugs.eclipse.org/bugs/show_bug.cgi?id=18936
			if (!fImageInitialized) {
				initializeImages();
				if (!isQuickFixableStateSet())
					setQuickFixable(isProblem() && indicateQuixFixableProblems() && JavaCorrectionProcessor.hasCorrections(this)); // no light bulb for tasks
				if (isQuickFixable()) {
					if (JavaMarkerAnnotation.ERROR_ANNOTATION_TYPE.equals(getType()))
						fImage= fgQuickFixErrorImage;
					else
						fImage= fgQuickFixImage;
				} else {
					String type= getType();
					if (JavaMarkerAnnotation.TASK_ANNOTATION_TYPE.equals(type))
						fImage= fgTaskImage;
					else if (JavaMarkerAnnotation.INFO_ANNOTATION_TYPE.equals(type))
						fImage= fgInfoImage;
					else if (JavaMarkerAnnotation.WARNING_ANNOTATION_TYPE.equals(type))
						fImage= fgWarningImage;
					else if (JavaMarkerAnnotation.ERROR_ANNOTATION_TYPE.equals(type))
						fImage= fgErrorImage;
				}
				fImageInitialized= true;
			}
		}